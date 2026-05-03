# Email Alert Configuration
# To set up email alerts, create a .env file in the same directory with:
#
# EMAIL_SENDER=your_email@gmail.com
# EMAIL_PASSWORD=your_app_password
# EMAIL_RECIPIENT=recipient@email.com
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
#
# For Gmail, use an App Password (not your regular password):
# https://myaccount.google.com/apppasswords

import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Alert settings
CHECK_INTERVAL_HOURS = int(os.getenv("CHECK_INTERVAL_HOURS", "24"))  # Check daily
ALERT_LEAD_DAYS = int(os.getenv("ALERT_LEAD_DAYS", "7"))  # Alert 7 days before milestone
