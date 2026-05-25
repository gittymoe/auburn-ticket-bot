import os
import re
import smtplib
import requests
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
ALERT_EMAIL = os.environ["ALERT_EMAIL"]

URL = "https://gametime.co/college-football/tigers-at-volunteers-tickets/10-3-2026-knoxville-tn-neyland-stadium/events/68d394609ae20cad877e77c9"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers, timeout=20)

results = []

if response.status_code == 200:

    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text()

    prices = re.findall(r"\$\d+", text)

    unique_prices = sorted(set(prices))

    if unique_prices:
        results.append("Possible ticket prices found:\n")

        for price in unique_prices[:20]:
            results.append(price)

    else:
        results.append("No prices detected.")

else:
    results.append(f"Failed with status code {response.status_code}")

message = "\n".join(results)

msg = MIMEText(message)

msg["Subject"] = "Auburn Ticket Price Scan"
msg["From"] = GMAIL_USER
msg["To"] = ALERT_EMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(GMAIL_USER, GMAIL_PASS)
    smtp.send_message(msg)

print("Price scan email sent.")
