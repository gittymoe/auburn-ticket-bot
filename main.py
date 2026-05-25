import os
import re
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
ALERT_EMAIL = os.environ["ALERT_EMAIL"]

SITES = {
    "Gametime": "https://gametime.co/college-football/tigers-at-volunteers-tickets/10-3-2026-knoxville-tn-neyland-stadium/events/68d394609ae20cad877e77c9",

    "TickPick": "https://www.tickpick.com/buy-tennessee-volunteers-vs-auburn-tigers-football-tickets-neyland-stadium-10-3-26-12pm/",

    "SeatGeek": "https://seatgeek.com/auburn-tigers-at-tennessee-volunteers-football-tickets/ncaa-football/2026-10-03-12-pm/6478154",

    "StubHub": "https://www.stubhub.com/tennessee-volunteers-football-knoxville-tickets-10-3-2026/event/156000000/"
}

all_results = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    for site_name, url in SITES.items():

        try:

            page = browser.new_page(
                viewport={"width": 1600, "height": 1400}
            )

            page.goto(url, timeout=90000)

            page.wait_for_timeout(12000)

            body_text = page.locator("body").inner_text()

            lines = []

            for line in body_text.splitlines():

                clean = line.strip()

                if clean:
                    lines.append(clean)

            ticket_blocks = []

            for i, line in enumerate(lines):

                if "$" in line:

                    nearby = lines[
               max(0, i - 4):min(len(lines), i + 5)

                    combined = " | ".join(nearby)

                   if (
    "row" in combined.lower()
    or "upper" in combined.lower()
    or "lower" in combined.lower()
    or "club" in combined.lower()
    or "section" in combined.lower()
    or "seat" in combined.lower()
    or "deal" in combined.lower()
    or "fees" in combined.lower()
    or "/ea" in combined.lower()
    or "ticket" in combined.lower()
    or "$" in combined
):

                        if combined not in ticket_blocks:
                            ticket_blocks.append(combined)

            all_results.append("")
            all_results.append("=" * 60)
            all_results.append(site_name.upper())
            all_results.append("=" * 60)
            all_results.append(f"Source Link: {url}")
            all_results.append("")

            if len(ticket_blocks) == 0:

                all_results.append(
                    "No structured ticket listings detected."
                )

            else:

                for idx, block in enumerate(ticket_blocks[:10], start=1):

                    all_results.append(f"Deal #{idx}")

                    all_results.append(block)

                    prices = re.findall(r"\$\d+", block)

                    if len(prices) > 0:

                        numeric_prices = []

                        for p_text in prices:

                            value = int(
                                p_text.replace("$", "")
                            )

                            numeric_prices.append(value)

                        cheapest = min(numeric_prices)

                        total_for_four = cheapest * 4

                        all_results.append(
                            f"Estimated Per Ticket: ${cheapest}"
                        )

                        all_results.append(
                            f"Estimated Total For 4 Tickets: ${total_for_four}"
                        )

                    lower_block = block.lower()

                    if "upper" in lower_block:
                        all_results.append("Area: Upper Level")

                    if "lower" in lower_block:
                        all_results.append("Area: Lower Level")

                    if "club" in lower_block:
                        all_results.append("Area: Club Level")

                    all_results.append(f"Buy Link: {url}")
                    all_results.append("")

            page.close()

        except Exception as e:

            all_results.append("")
            all_results.append("=" * 60)
            all_results.append(site_name.upper())
            all_results.append("=" * 60)
            all_results.append(f"FAILED TO SCAN SITE")
            all_results.append(str(e))
            all_results.append("")

    browser.close()

message = "\n".join(all_results)

msg = MIMEText(message)

msg["Subject"] = "Auburn vs Tennessee Ticket Deals"
msg["From"] = GMAIL_USER
msg["To"] = ALERT_EMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:

    smtp.login(GMAIL_USER, GMAIL_PASS)

    smtp.send_message(msg)

print("Multi-site ticket summary email sent.")
