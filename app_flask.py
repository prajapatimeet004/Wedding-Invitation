import sqlite3
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from database_manager import get_db_connection, init_db
from scheduler import check_and_send_reminders

app = Flask(__name__)
CORS(app) # Enable CORS for frontend requests

logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return "<h1>Python Event Server is Running! ✅</h1><p>You can now use the RSVP form on your wedding website.</p>"

@app.route('/trigger-reminders', methods=['GET'])
def trigger_reminders_manual():
    """
    Call this URL from a free cron service (like cron-job.org) 
    to automate emails without running the script 24/7 on your PC.
    """
    try:
        check_and_send_reminders()
        return jsonify({"status": "success", "message": "Checked for reminders."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all events
        cursor.execute("SELECT id FROM events")
        events = cursor.fetchall()
        
        # Register for each event
        for event in events:
            # Check if already registered
            cursor.execute("SELECT id FROM reminders WHERE email = ? AND event_id = ?", (email, event['id']))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO reminders (email, name, event_id, status) VALUES (?, ?, ?, 'pending')", 
                               (email, data.get('name', 'Guest'), event['id']))
        
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Reminders set successfully!"})
    
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    init_db() # Ensure DB is ready
    app.run(port=5000, debug=True)
