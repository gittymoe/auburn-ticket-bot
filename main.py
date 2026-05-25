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

#
# TRY TO APPLY 4-TICKET FILTER
#

try:

    page.get_by_text("Filters").click(timeout=5000)

    page.wait_for_timeout(3000)

    possible_quantity_buttons = [
        "4 Tickets",
        "4 tickets",
        "Qty 4",
        "Quantity 4",
        "4+"
    ]

    for label in possible_quantity_buttons:

        try:
            page.get_by_text(label).click(timeout=2000)
            break
        except:
            pass

    page.wait_for_timeout(2000)

    possible_apply_buttons = [
        "Apply",
        "Show Results",
        "Done"
    ]

    for label in possible_apply_buttons:

        try:
            page.get_by_text(label).click(timeout=2000)
            break
        except:
            pass

    page.wait_for_timeout(5000)

    results.append("4-ticket filter attempted successfully.\n")

except Exception as e:

    results.append(f"Could not apply 4-ticket filter: {str(e)}\n")

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

results.append("Auburn vs Tennessee Ticket Deal Summary\n")

results.append("Source: Gametime")
results.append(f"Event Link: {EVENT_URL}\n")

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

msg["Subject"] = "Auburn 4-Ticket Deal Scan"
msg["From"] = GMAIL_USER
msg["To"] = ALERT_EMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
smtp.login(GMAIL_USER, GMAIL_PASS)
smtp.send_message(msg)

print("4-ticket filtered scan complete.")
