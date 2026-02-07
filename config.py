import os

# Database Settings
# Use absolute path so it works from any terminal location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "wedding_reminders.db")

# SMTP Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USE_TLS = True
SMTP_USER = "rainsound004@gmail.com"  # Replace with your email
SMTP_PASS = "rzur tstt kkew dvbq"     # Replace with your Gmail App Password
FROM_NAME = "Hemangi & Manish Wedding"

# Reminder Settings
REMINDER_INTERVAL_MINUTES = 60  # Send reminder 1 hour before
CRON_WINDOW_MINUTES = 5         # Search window for the cron job
