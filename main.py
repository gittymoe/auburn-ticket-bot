import os
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
ALERT_EMAIL = os.environ["ALERT_EMAIL"]

URL = "https://gametime.co/college-football/tigers-at-volunteers-tickets/10-3-2026-knoxville-tn-neyland-stadium/events/68d394609ae20cad877e77c9"

results = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(URL, timeout=60000)

    page.wait_for_timeout(10000)

    text = page.locator("body").inner_text()

    browser.close()

prices = []

for line in text.splitlines():

    if "$" in line:

        cleaned = line.strip()

        if len(cleaned) < 80:
            prices.append(cleaned)

unique_prices = list(dict.fromkeys(prices))

results.append("Possible Ticket Listings Found:\n")

for item in unique_prices[:40]:
    results.append(item)

message = "\n".join(results)

msg = MIMEText(message)

msg["Subject"] = "Auburn Ticket Browser Scan"
msg["From"] = GMAIL_USER
msg["To"] = ALERT_EMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(GMAIL_USER, GMAIL_PASS)
    smtp.send_message(msg)

print("Browser scan complete.")
