# NYC → Seattle flight price monitor

This checks one-way economy fares every two hours for Dec 20–24, 2026:

- Origins: JFK, LGA, EWR, HPN, SWF
- Destinations: SEA, PAE
- Alert when the lowest fare is below $550
- After a successful email, the alert threshold becomes the newly found price

## Important fare limitation

The zero-cost source is `fast-flights`, an unofficial Google Flights-compatible
fetcher. Google does not provide a public fare-pricing API. Its free result model
reports economy prices but not the final branded fare name, so the email asks you
to confirm **Main/Main Cabin** rather than **Basic Economy** on the booking page.
Do not treat the alert as a guaranteed bookable Main Cabin quote.

## Free hosting: GitHub Actions

The included workflow runs at minute 17 every second hour. Standard GitHub-hosted
Actions are free for public repositories; private repositories consume the
account's included minutes. Scheduled workflows can be delayed during busy
periods and are disabled after 60 days without repository activity in public
repositories, so keep an eye on the Actions tab.

1. Create a GitHub repository and push this folder.
2. In **Settings → Secrets and variables → Actions**, add:
   - `ALERT_EMAIL`: where alerts should go
   - `SMTP_USERNAME`: Gmail address (or another SMTP username)
   - `SMTP_PASSWORD`: Gmail app password, not the normal account password
   - Optional: `SMTP_FROM`, `SMTP_HOST`, `SMTP_PORT`
3. In **Actions → Monitor flight price**, choose **Run workflow** once to verify it.

For Gmail, the defaults are `smtp.gmail.com` on port `465`. Google accounts with
2-Step Verification can create an app password. Other SMTP providers work by
setting the host and port secrets.

## Local test

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests
ALERT_EMAIL=you@example.com SMTP_USERNAME=you@example.com python flight_monitor.py --dry-run
```

Edit `config.json` to change dates, airports, stops, or trip assumptions. The
workflow commits `state.json` only when its status or threshold changes.
