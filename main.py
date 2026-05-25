import os
import smtplib
from email.mime.text import MIMEText

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
ALERT_EMAIL = os.environ["ALERT_EMAIL"]

message = """
Auburn vs Tennessee Ticket Watch

Current ticket sources:

StubHub:
https://www.stubhub.com/

Gametime:
https://gametime.co/

Ticketmaster:
https://www.ticketmaster.com/

This is your first automated bot test.
"""

msg = MIMEText(message)

msg["Subject"] = "Auburn Ticket Bot Test"
msg["From"] = GMAIL_USER
msg["To"] = ALERT_EMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(GMAIL_USER, GMAIL_PASS)
    smtp.send_message(msg)

print("Email sent successfully.")
