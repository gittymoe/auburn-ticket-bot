import os
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
ALERT_EMAIL = os.environ["ALERT_EMAIL"]

SITE_NAME = "Gametime"

EVENT_URL = "https://gametime.co/college-football/tigers-at-volunteers-tickets/10-3-2026-knoxville-tn-neyland-stadium/events/68d394609ae20cad877e77c9"

results = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(EVENT_URL, timeout=60000)

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

results.append("Auburn vs Tennessee Ticket Deals\n")

results.append(f"Source Site: {SITE_NAME}")
results.append(f"Direct Link: {EVENT_URL}\n")

for idx, listing in enumerate(ticket_lines[:20], start=1):

    results.append(f"Listing #{idx}")
    results.append(listing)
    results.append(f"Buy Here: {EVENT_URL}")
    results.append("")

message = "\n".join(results)

msg = MIMEText(message)

msg["Subject"] = "Auburn Ticket Deals With Links"
msg["From"] = GMAIL_USER
msg["To"] = ALERT_EMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(GMAIL_USER, GMAIL_PASS)
    smtp.send_message(msg)

print("Enhanced ticket email sent.")
