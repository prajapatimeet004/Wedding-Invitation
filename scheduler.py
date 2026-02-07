import smtplib
from email.message import EmailMessage
import sqlite3
import datetime
import time
import logging
from config import *
from database_manager import get_db_connection

# Setup logging
logging.basicConfig(
    filename='reminders.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def send_email(to_email, event_name, event_date, location, minutes_left):
    # Dynamic subject based on time
    if minutes_left <= 60:
        time_text = f"{minutes_left} minutes"
    else:
        hours = round(minutes_left / 60, 1)
        time_text = f"{hours} hours"
        
    msg = EmailMessage()
    msg['Subject'] = f"Reminder: {event_name} begins in {time_text}! ✨"
    msg['From'] = f"{FROM_NAME} <{SMTP_USER}>"
    msg['To'] = to_email

    # HTML Body
    body = f"""
    <html>
    <body style="font-family: 'Playfair Display', serif; color: #333; background-color: #fffcf0; padding: 20px;">
        <div style="border: 2px solid #800000; padding: 25px; border-radius: 15px; background: #ffffff; max-width: 600px; margin: auto;">
            <h2 style="color: #800000; text-align: center;">Wedding Ceremony Reminder ✨</h2>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <p>Hi there,</p>
            <p>This is a friendly reminder that the <strong>{event_name}</strong> is about to begin in roughly <strong>{time_text}</strong>!</p>
            <div style="background: #fdf5f5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Time:</strong> {event_date}</p>
                <p style="margin: 5px 0;"><strong>Location:</strong> {location}</p>
                <p style="margin: 15px 0 5px 0; text-align: center;">
                    <a href="https://maps.app.goo.gl/tH7q9DNDN5v6P37q7" style="background-color: #800000; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        📍 View on Google Maps
                    </a>
                </p>
            </div>
            <p>We can't wait to celebrate with you.</p>
            <p style="font-size: 14px; color: #777; border-top: 1px solid #eee; padding-top: 15px; margin-top: 30px; text-align: center;">
                Warm Regards,<br>
                <strong>Hemangi & Manish</strong>
            </p>
        </div>
    </body>
    </html>
    """
    msg.set_content(f"Reminder: {event_name} begins in {time_text} at {location}. We look forward to seeing you!")
    msg.add_alternative(body, subtype='html')

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            if SMTP_USE_TLS:
                server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {e}")
        return False

def check_and_send_reminders():
    logging.info("Checking for upcoming events...")
    conn = get_db_connection()
    cursor = conn.cursor()

    now = datetime.datetime.now()
    
    # Logic: Look for events starting anytime from NOW until NOW + 65 Minutes
    # This covers "late registrations" (e.g., event is in 10 mins) and standard queries (event in 60 mins)
    window_start = now
    window_end = now + datetime.timedelta(minutes=65)

    cursor.execute("""
        SELECT r.id as reminder_id, r.email, e.name as event_name, e.event_date, e.location 
        FROM reminders r
        JOIN events e ON r.event_id = e.id
        WHERE r.status = 'pending' 
        AND e.event_date BETWEEN ? AND ?
    """, (window_start.strftime('%Y-%m-%d %H:%M:%S'), window_end.strftime('%Y-%m-%d %H:%M:%S')))

    reminders = cursor.fetchall()
    
    if not reminders:
        print("No reminders are due at this moment.")
        logging.info("No reminders due at this time.")
    
    for reminder in reminders:
        # Calculate exactly how many minutes are left
        event_time = datetime.datetime.strptime(reminder['event_date'], '%Y-%m-%d %H:%M:%S')
        delta = event_time - now
        minutes_left = int(delta.total_seconds() / 60)
        
        minutes_left = max(1, minutes_left) # Prevent '0 minutes' or negative

        print(f"Sending reminder to {reminder['email']} ({minutes_left} mins remaining)...")
        success = send_email(
            reminder['email'], 
            reminder['event_name'], 
            reminder['event_date'], 
            reminder['location'],
            minutes_left
        )
        
        if success:
            cursor.execute("UPDATE reminders SET status = 'sent' WHERE id = ?", (reminder['reminder_id'],))
            conn.commit()
            print(f"Success! Reminder sent to {reminder['email']}")
            logging.info(f"Successfully sent reminder to {reminder['email']} for {reminder['event_name']}")
        else:
            print(f"Failed! Check reminders.log for errors.")
            logging.error(f"Failed to send reminder for ID {reminder['reminder_id']}")

    conn.close()
    print("\nProcess finished.")

if __name__ == "__main__":
    print("===================================================")
    print("  WEDDING REMINDER SCHEDULER IS RUNNING")
    print("  (Do not close this window)")
    print("===================================================")
    
    while True:
        try:
            check_and_send_reminders()
        except Exception as e:
            print(f"Error in scheduler loop: {e}")
            logging.error(f"Scheduler Loop Error: {e}")
        
        # Wait for 5 minutes before next check
        print("Waiting 5 minutes for next check...")
        time.sleep(300)
