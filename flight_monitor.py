from __future__ import annotations

import argparse
import json
import os
import smtplib
import ssl
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Iterable
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
STATE_PATH = ROOT / "state.json"


@dataclass(frozen=True)
class Deal:
    price: int
    travel_date: str
    origin: str
    destination: str
    airlines: list[str]
    stops: int
    booking_url: str


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def dates_around(target: str, flex_days: int) -> Iterable[str]:
    center = date.fromisoformat(target)
    for offset in range(-flex_days, flex_days + 1):
        yield (center + timedelta(days=offset)).isoformat()


def dates_between(start: str, end: str) -> Iterable[str]:
    current = date.fromisoformat(start)
    final = date.fromisoformat(end)
    while current <= final:
        yield current.isoformat()
        current += timedelta(days=1)


def search_deals(config: dict[str, Any]) -> list[Deal]:
    from fast_flights import FlightQuery, Passengers, create_query, get_flights

    deals: list[Deal] = []
    travel_dates = (
        dates_between(config["start_date"], config["end_date"])
        if "start_date" in config
        else dates_around(config["target_date"], config["date_flex_days"])
    )
    for travel_date in travel_dates:
        for origin in config["origin_airports"]:
            for destination in config["destination_airports"]:
                query = create_query(
                    flights=[
                        FlightQuery(
                            date=travel_date,
                            from_airport=origin,
                            to_airport=destination,
                        )
                    ],
                    seat=config["fare"],
                    trip=config["trip_type"],
                    passengers=Passengers(adults=config["passengers"]),
                    language="en-US",
                    currency=config["currency"],
                    max_stops=config["max_stops"],
                )
                for result in get_flights(query):
                    segments = result.flights
                    if not segments:
                        continue
                    deals.append(
                        Deal(
                            price=int(result.price),
                            travel_date=travel_date,
                            origin=segments[0].from_airport.code,
                            destination=segments[-1].to_airport.code,
                            airlines=list(result.airlines),
                            stops=max(0, len(segments) - 1),
                            booking_url=query.url(),
                        )
                    )
    return deals


def build_email(
    deal: Deal, old_threshold: int, recipient: str | None = None
) -> EmailMessage:
    recipient = recipient or required_env("ALERT_EMAIL")
    sender = os.getenv("SMTP_FROM", os.getenv("SMTP_USERNAME", ""))
    if not sender:
        raise RuntimeError("Set SMTP_FROM or SMTP_USERNAME")

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = (
        f"Flight price alert: ${deal.price} {deal.origin} → {deal.destination}"
    )
    airline_text = ", ".join(deal.airlines) or "Unknown airline"
    message.set_content(
        f"""A lower NYC-area → Seattle-area economy fare was found.

Price: ${deal.price} (previous threshold: ${old_threshold})
Date: {deal.travel_date}
Route: {deal.origin} → {deal.destination}
Airline(s): {airline_text}
Stops: {deal.stops}

Open Google Flights:
{deal.booking_url}

The monitor's next alert threshold is now ${deal.price}.

Important: the free data source exposes economy prices but not the final branded
fare name. Confirm that the booking page says Main/Main Cabin—not Basic Economy—
before buying.
"""
    )
    return message


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def send_email(message: EmailMessage) -> None:
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "465"))
    username = required_env("SMTP_USERNAME")
    password = required_env("SMTP_PASSWORD")
    with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context()) as server:
        server.login(username, password)
        server.send_message(message)


def api_request(method: str = "GET", body: dict[str, Any] | None = None) -> Any:
    data = json.dumps(body).encode() if body is not None else None
    request = Request(
        required_env("MONITOR_API_URL"),
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {required_env('MONITOR_API_KEY')}",
            "Content-Type": "application/json",
            "User-Agent": "Farewatch/1.0 (+https://github.com/DolphinWorld/cheapticket)",
        },
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def run_remote(*, dry_run: bool = False) -> int:
    for monitor in api_request():
        config = {
            "origin_airports": [monitor["departure"]],
            "destination_airports": [monitor["arrival"]],
            "start_date": monitor["startDate"],
            "end_date": monitor["endDate"],
            "trip_type": "one-way",
            "currency": "USD",
            "passengers": 1,
            "max_stops": 1,
            "fare": "economy",
        }
        deals = search_deals(config)
        cheapest = min(deals, key=lambda item: item.price) if deals else None
        if not cheapest or cheapest.price >= int(monitor["threshold"]):
            print(f"Monitor {monitor['id']}: no alert")
            continue
        message = build_email(
            cheapest, int(monitor["threshold"]), monitor["email"]
        )
        if dry_run:
            print(message)
        else:
            send_email(message)
            api_request("PATCH", {"id": monitor["id"], "threshold": cheapest.price})
    return 0


def run(*, dry_run: bool = False) -> int:
    config = load_json(CONFIG_PATH)
    state = load_json(STATE_PATH)
    now = datetime.now(timezone.utc).isoformat()
    try:
        deals = search_deals(config)
        cheapest = min(deals, key=lambda item: item.price) if deals else None
        state["last_checked_at"] = now
        state["last_price"] = cheapest.price if cheapest else None
        state["last_error"] = None

        if cheapest and cheapest.price < int(state["threshold"]):
            message = build_email(cheapest, int(state["threshold"]))
            if dry_run:
                print(message)
            else:
                send_email(message)
                state["threshold"] = cheapest.price
                state["last_deal"] = asdict(cheapest)
        else:
            current = cheapest.price if cheapest else "no results"
            print(f"No alert. Cheapest: {current}; threshold: {state['threshold']}")
        write_json(STATE_PATH, state)
        return 0
    except Exception as error:
        state["last_checked_at"] = now
        state["last_error"] = f"{type(error).__name__}: {error}"
        write_json(STATE_PATH, state)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor NYC-area to Seattle fares")
    parser.add_argument("--dry-run", action="store_true", help="print instead of email")
    args = parser.parse_args()
    runner = run_remote if os.getenv("MONITOR_API_URL") else run
    raise SystemExit(runner(dry_run=args.dry_run))
