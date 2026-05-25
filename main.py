import os
import re
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
ALERT_EMAIL = os.environ["ALERT_EMAIL"]

EVENT_URL = "https://gametime.co/college-football/tigers-at-volunteers-tickets/10-3-2026-knoxville-tn-neyland-stadium/events/68d394609ae20cad877e77c9"

results = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page(viewport={"width": 1600, "height": 1400})

    page.goto(EVENT_URL, timeout=60000)

    page.wait_for_timeout(15000)

    body_text = page.locator("body").inner_text()

    browser.close()

lines = [line.strip() for line in body_text.splitlines() if line.strip()]

ticket_blocks = []

deal_number = 1

for block in ticket_blocks:

    block_lower = block.lower()

    has_four = (
        "4 tickets" in block_lower
        or "qty 4" in block_lower
        or "quantity 4" in block_lower
        or "4+" in block_lower
    )

   if has_four:
    results.append("Likely supports 4 seats together")
else:
    results.append("Seat quantity not confirmed")

    results.append(f"Deal #{deal_number}")

    clean_block = block.replace("  ", " ")

    results.append(clean_block)

    price_search = re.findall(r"\$\d+", block)

    if price_search:

        numeric_prices = [
            int(p.replace("$", ""))
            for p in price_search
        ]

        cheapest = min(numeric_prices)

        total_price = cheapest * 4

        results.append(f"Price Per Ticket: ${cheapest}")
        results.append(f"Estimated Total For 4: ${total_price}")

    if "Upper" in block:
        results.append("Area: Upper Level")

    if "Lower" in block:
        results.append("Area: Lower Level")

    results.append(f"Buy Link: {EVENT_URL}")

    results.append("")

    deal_number += 1

if deal_number == 1:

    results.append("No obvious 4-seat listings detected.")

results.append(f"Source: Gametime")
results.append(f"Event Link: {EVENT_URL}\n")

if not ticket_blocks:

    results.append("No structured ticket blocks found.")

else:

    for idx, block in enumerate(ticket_blocks[:20], start=1):

        results.append(f"Deal #{idx}")

        clean_block = block.replace("  ", " ")

        results.append(clean_block)

        price_search = re.findall(r"\$\d+", block)

        if price_search:

            numeric_prices = [
                int(p.replace("$", ""))
                for p in price_search
            ]

            cheapest = min(numeric_prices)

            results.append(f"Detected Price: ${cheapest}")

        if "Upper" in block:
            results.append("Area: Upper Level")

        if "Lower" in block:
            results.append("Area: Lower Level")

        results.append(f"Buy Link: {EVENT_URL}")

        results.append("")

message = "\n".join(results)

msg = MIMEText(message)

msg["Subject"] = "Improved Auburn Ticket Deal Summary"
msg["From"] = GMAIL_USER
msg["To"] = ALERT_EMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(GMAIL_USER, GMAIL_PASS)
    smtp.send_message(msg)

print("Improved ticket summary sent.")
