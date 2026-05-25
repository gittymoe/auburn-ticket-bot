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

```
browser = p.chromium.launch(headless=True)

page = browser.new_page(
    viewport={"width": 1600, "height": 1400}
)

page.goto(EVENT_URL, timeout=60000)

page.wait_for_timeout(10000)

body_text = page.locator("body").inner_text()

browser.close()
```

lines = [
line.strip()
for line in body_text.splitlines()
if line.strip()
]

ticket_blocks = []

for i, line in enumerate(lines):

```
if re.search(r"\$\d+", line):

    nearby = lines[max(0, i-1): min(len(lines), i+2)]

    combined = " | ".join(nearby)

    if (
        "Includes Fees" in combined
        or "Upper" in combined
        or "Lower" in combined
        or "Row" in combined
    ):

        if combined not in ticket_blocks:
            ticket_blocks.append(combined)
```

results.append("Auburn vs Tennessee Ticket Deal Summary")
results.append("")
results.append("Source: Gametime")
results.append(f"Event Link: {EVENT_URL}")
results.append("")

if not ticket_blocks:

```
results.append("No ticket listings found.")
```

else:

```
for idx, block in enumerate(ticket_blocks[:20], start=1):

    results.append(f"Deal #{idx}")

    results.append(block)

    prices = re.findall(r"\$\d+", block)

    if prices:

        numeric = [
            int(p.replace("$", ""))
            for p in prices
        ]

        cheapest = min(numeric)

        results.append(f"Price Per Ticket: ${cheapest}")
        results.append(f"Estimated Total For 4: ${cheapest * 4}")

    if "Upper" in block:
        results.append("Area: Upper Level")

    if "Lower" in block:
        results.append("Area: Lower Level")

    results.append(f"Buy Link: {EVENT_URL}")

    results.append("")
```

message = "\n".join(results)

msg = MIMEText(message)

msg["Subject"] = "Auburn Ticket Deal Summary"
msg["From"] = GMAIL_USER
msg["To"] = ALERT_EMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
smtp.login(GMAIL_USER, GMAIL_PASS)
smtp.send_message(msg)

print("Ticket summary sent.")
