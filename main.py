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

    page.wait_for_timeout(12000)

    body_text = page.locator("body").inner_text()

    browser.close()

lines = body_text.splitlines()

ticket_lines = []

for i, line in enumerate(lines):

    line = line.strip()

    if "/ea" in line or "$" in line:

        context = lines[max(0, i-2): min(len(lines), i+3)]

        combined = " | ".join(context)

        if combined not in ticket_lines:
            ticket_lines.append(combined)

results.append("Auburn vs Tennessee Ticket Listings\n")

for listing in ticket_lines[:25]:
    results.append(listing)
    results.append("\n")

message = "\n".join(results)

msg = MIMEText(message)

msg["Subject"] = "Structured Auburn Ticket Scan"
msg["From"] = GMAIL_USER
msg["To"] = ALERT_EMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(GMAIL_USER, GMAIL_PASS)
    smtp.send_message(msg)

print("Structured ticket scan sent.")
