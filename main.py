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

CARD_SELECTORS = [
    '[class*="ticket"]',
    '[class*="listing"]',
    '[class*="event"]',
    '[class*="seat"]',
    '[data-testid*="listing"]',
    '[data-testid*="ticket"]',
    'article',
    'li'
]

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    for site_name, url in SITES.items():

        try:

            page = browser.new_page(
                viewport={"width": 1600, "height": 1400}
            )

            page.goto(url, timeout=90000)

            page.wait_for_timeout(15000)

            ticket_blocks = []

            #
            # Try structured selectors first
            #

            for selector in CARD_SELECTORS:

                try:

                    elements = page.locator(selector)

                    count = min(elements.count(), 40)

                    for i in range(count):

                        try:

                            text = elements.nth(i).inner_text()

                            clean = text.strip()

                            if (
                                "$" in clean
                                and len(clean) > 20
                                and len(clean) < 1200
                            ):

                                lower = clean.lower()

                                if (
                                    "section" in lower
                                    or "row" in lower
                                    or "deal" in lower
                                    or "ticket" in lower
                                    or "seat" in lower
                                    or "fees" in lower
                                ):

                                    if clean not in ticket_blocks:
                                        ticket_blocks.append(clean)

                        except:
                            pass

                except:
                    pass

            #
            # Fallback to body text if needed
            #

            if len(ticket_blocks) == 0:

                body_text = page.locator("body").inner_text()

                lines = [
                    line.strip()
                    for line in body_text.splitlines()
                    if line.strip()
                ]

                for i, line in enumerate(lines):

                    if "$" in line:

                        nearby = lines[
                            max(0, i - 3):min(len(lines), i + 5)
                        ]

                        combined = " | ".join(nearby)

                        if combined not in ticket_blocks:
                            ticket_blocks.append(combined)

            #
            # Build email output
            #

            all_results.append("")
            all_results.append("=" * 60)
            all_results.append(site_name.upper())
            all_results.append("=" * 60)
            all_results.append(f"Source Link: {url}")
            all_results.append("")

            if len(ticket_blocks) == 0:

                all_results.append(
                    "No ticket listings detected."
                )

            else:

                for idx, block in enumerate(ticket_blocks[:10], start=1):

                    all_results.append(f"Deal #{idx}")

                    compact = " ".join(block.split())

                    all_results.append(compact)

                    prices = re.findall(r"\$\d+", compact)

                    if prices:

                        numeric = [
                            int(p.replace("$", ""))
                            for p in prices
                        ]

                        cheapest = min(numeric)

                        all_results.append(
                            f"Estimated Per Ticket: ${cheapest}"
                        )

                        all_results.append(
                            f"Estimated Total For 5: ${cheapest * 5}"
                        )

                    all_results.append(f"Buy Link: {url}")
                    all_results.append("")

            page.close()

        except Exception as e:

            all_results.append("")
            all_results.append("=" * 60)
            all_results.append(site_name.upper())
            all_results.append("=" * 60)
            all_results.append("FAILED TO SCAN SITE")
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
