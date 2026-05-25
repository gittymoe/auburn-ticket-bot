import os
import json
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
ALERT_EMAIL = os.environ["ALERT_EMAIL"]

EVENT_URL = "https://gametime.co/college-football/tigers-at-volunteers-tickets/10-3-2026-knoxville-tn-neyland-stadium/events/68d394609ae20cad877e77c9"

captured_data = []

def handle_response(response):

    try:
        url = response.url

        if "graphql" in url.lower() or "listing" in url.lower():

            content_type = response.headers.get("content-type", "")

            if "application/json" in content_type:

                data = response.json()

                captured_data.append({
                    "url": url,
                    "data": data
                })

    except Exception:
        pass

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.on("response", handle_response)

    page.goto(EVENT_URL, timeout=60000)

    page.wait_for_timeout(15000)

    browser.close()

results = []

results.append("Auburn vs Tennessee Structured Ticket Data\n")

listing_count = 0

for item in captured_data:

    data_str = json.dumps(item["data"])

    if "$" in data_str or "price" in data_str.lower():

        results.append(f"Data Source: {item['url'][:120]}")
        results.append("")

        results.append(data_str[:4000])
        results.append("\n=========================\n")

        listing_count += 1

    if listing_count >= 5:
        break

if listing_count == 0:
    results.append("No structured listing JSON found.")

message = "\n".join(results)

msg = MIMEText(message)

msg["Subject"] = "Structured Auburn Ticket JSON Scan"
msg["From"] = GMAIL_USER
msg["To"] = ALERT_EMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(GMAIL_USER, GMAIL_PASS)
    smtp.send_message(msg)

print("Structured JSON scan complete.")
