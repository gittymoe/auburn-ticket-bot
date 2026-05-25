import os
import smtplib
import requests
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
ALERT_EMAIL = os.environ["ALERT_EMAIL"]

sites = {
    "StubHub": "https://www.stubhub.com/tennessee-volunteers-football-knoxville-tickets-10-3-2026/event/107140307/",
    "Gametime": "https://gametime.co/college-football/tigers-at-volunteers-tickets/10-3-2026-knoxville-tn-neyland-stadium/events/68d394609ae20cad877e77c9",
    "Ticketmaster": "https://www.ticketmaster.com/"
}

results = []

headers = {
    "User-Agent": "Mozilla/5.0"
}

for site, url in sites.items():
    try:
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            title = soup.title.string if soup.title else "No title found"

            results.append(
                f"{site}\n"
                f"URL: {url}\n"
                f"Page Title: {title}\n"
            )

        else:
            results.append(
                f"{site}\n"
                f"Failed with status code {response.status_code}\n"
            )

    except Exception as e:
        results.append(
            f"{site}\n"
            f"Error: {str(e)}\n"
        )

message = "\n\n".join(results)

msg = MIMEText(message)

msg["Subject"] = "Auburn vs Tennessee Ticket Scan"
msg["From"] = GMAIL_USER
msg["To"] = ALERT_EMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(GMAIL_USER, GMAIL_PASS)
    smtp.send_message(msg)

print("Ticket scan email sent.")
