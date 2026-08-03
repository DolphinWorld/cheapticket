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

AIRPORT_NAMES = {
    "JFK": "John F. Kennedy International",
    "LGA": "LaGuardia",
    "EWR": "Newark Liberty International",
    "SEA": "Seattle-Tacoma International",
    "PAE": "Seattle Paine Field",
}


@dataclass(frozen=True)
class Deal:
    price: int
    travel_date: str
    departure_at: str
    origin: str
    destination: str
    airlines: list[str]
    stops: int
    booking_url: str
    return_at: str | None = None


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


def flight_datetime(value: Any) -> str | None:
    """Return an ISO timestamp, or None when a provider result is incomplete."""
    try:
        parts = (*value.date, *value.time)
        if any(part is None for part in parts):
            return None
        return datetime(*parts).isoformat(timespec="minutes")
    except (AttributeError, TypeError, ValueError):
        return None


def search_deals(config: dict[str, Any]) -> list[Deal]:
    from fast_flights import FlightQuery, Passengers, create_query, get_flights

    deals: list[Deal] = []
    travel_dates = list(
        dates_between(config["start_date"], config["end_date"])
        if "start_date" in config
        else dates_around(config["target_date"], config["date_flex_days"])
    )
    date_pairs: list[tuple[str, str | None]] = [(item, None) for item in travel_dates]
    if config["trip_type"] == "round-trip":
        return_dates = list(
            dates_between(config["return_start_date"], config["return_end_date"])
        )
        date_pairs = [
            (outbound, returning)
            for outbound in travel_dates
            for returning in return_dates
            if returning >= outbound
        ]
    for travel_date, return_date in date_pairs:
        for origin in config["origin_airports"]:
            for destination in config["destination_airports"]:
                flights = [
                    FlightQuery(
                        date=travel_date,
                        from_airport=origin,
                        to_airport=destination,
                        airlines=config.get("airlines"),
                    )
                ]
                if return_date:
                    flights.append(
                        FlightQuery(
                            date=return_date,
                            from_airport=destination,
                            to_airport=origin,
                            airlines=config.get("airlines"),
                        )
                    )
                query = create_query(
                    flights=flights,
                    seat=config["fare"],
                    trip=config["trip_type"],
                    passengers=Passengers(adults=config["passengers"]),
                    language="en-US",
                    currency=config["currency"],
                    max_stops=config["max_stops"],
                )
                return_at_hint = None
                if return_date:
                    return_query = create_query(
                        flights=[
                            FlightQuery(
                                date=return_date,
                                from_airport=destination,
                                to_airport=origin,
                                airlines=config.get("airlines"),
                            )
                        ],
                        seat=config["fare"],
                        trip="one-way",
                        passengers=Passengers(adults=config["passengers"]),
                        language="en-US",
                        currency=config["currency"],
                        max_stops=config["max_stops"],
                    )
                    eligible_returns = []
                    for return_offer in get_flights(return_query):
                        if not return_offer.flights:
                            continue
                        returning = return_offer.flights[0].departure
                        candidate = flight_datetime(returning)
                        if candidate is None:
                            continue
                        if config["return_start_at"] <= candidate <= config["return_end_at"]:
                            eligible_returns.append(candidate)
                    if not eligible_returns:
                        continue
                    return_at_hint = min(eligible_returns)
                for result in get_flights(query):
                    segments = result.flights
                    if not segments:
                        continue
                    departure = segments[0].departure
                    departure_at = flight_datetime(departure)
                    if departure_at is None:
                        continue
                    if config.get("start_at") and departure_at < config["start_at"]:
                        continue
                    if config.get("end_at") and departure_at > config["end_at"]:
                        continue
                    return_at = return_at_hint
                    deals.append(
                        Deal(
                            price=int(result.price),
                            travel_date=travel_date,
                            departure_at=departure_at,
                            origin=segments[0].from_airport.code,
                            destination=segments[-1].to_airport.code,
                            airlines=list(result.airlines),
                            stops=max(0, len(segments) - 1),
                            booking_url=query.url(),
                            return_at=return_at,
                        )
                    )
    return deals


def build_email(
    deal: Deal,
    old_threshold: int,
    recipient: str | None = None,
    watch_name: str = "All airlines",
) -> EmailMessage:
    recipient = recipient or required_env("ALERT_EMAIL")
    sender = os.getenv("SMTP_FROM") or os.getenv("SMTP_USERNAME", "")
    if not sender:
        raise RuntimeError("Set SMTP_FROM or SMTP_USERNAME")

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = (
        f"{watch_name} alert: ${deal.price} {deal.origin} → {deal.destination}"
    )
    airline_text = ", ".join(deal.airlines) or "Unknown airline"
    message.set_content(
        f"""A lower economy fare was found.

Watch: {watch_name}
Price: ${deal.price} (previous threshold: ${old_threshold})
Departure: {deal.departure_at}
{f"Return window availability found from: {deal.return_at}" if deal.return_at else "Trip: One way"}
Route: {deal.origin} ({AIRPORT_NAMES.get(deal.origin, "airport")}) → {deal.destination} ({AIRPORT_NAMES.get(deal.destination, "airport")})
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
    host = os.getenv("SMTP_HOST") or "smtp.gmail.com"
    port = int(os.getenv("SMTP_PORT") or "465")
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
        base_config = {
            "origin_airports": [monitor["departure"]],
            "destination_airports": [monitor["arrival"]],
            "start_date": monitor["startDate"],
            "end_date": monitor["endDate"],
            "start_at": f"{monitor['startDate']}T{monitor['startTime']}",
            "end_at": f"{monitor['endDate']}T{monitor['endTime']}",
            "trip_type": "one-way",
            "currency": "USD",
            "passengers": 1,
            "max_stops": 1,
            "fare": "economy",
        }
        if monitor.get("tripType") == "round-trip":
            base_config.update(
                {
                    "trip_type": "round-trip",
                    "return_start_date": monitor["returnStartDate"],
                    "return_end_date": monitor["returnEndDate"],
                    "return_start_at": f"{monitor['returnStartDate']}T{monitor['returnStartTime']}",
                    "return_end_at": f"{monitor['returnEndDate']}T{monitor['returnEndTime']}",
                }
            )
        checks = [
            ("all", "All airlines", int(monitor["threshold"]), base_config),
        ]
        if monitor.get("airline"):
            checks.append((
                "airline",
                f"Preferred airline {monitor['airline']}",
                int(monitor["airlineThreshold"]),
                {**base_config, "airlines": [monitor["airline"]]},
            ))
        for threshold_type, watch_name, threshold, config in checks:
            deals = search_deals(config)
            cheapest = min(deals, key=lambda item: item.price) if deals else None
            if not cheapest or cheapest.price >= threshold:
                print(f"Monitor {monitor['id']} {threshold_type}: no alert")
                continue
            message = build_email(
                cheapest, threshold, monitor["email"], watch_name
            )
            if dry_run:
                print(message)
            else:
                send_email(message)
                api_request(
                    "PATCH",
                    {
                        "id": monitor["id"],
                        "threshold": cheapest.price,
                        "thresholdType": threshold_type,
                    },
                )
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
