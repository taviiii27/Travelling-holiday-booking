import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_db_connection  # your DB connector
from email_utils import send_email  # your email sender

app = Flask(__name__)
CORS(app)

CLIENT_FILE = 'clients.json'

# Load or initialize clients list
if os.path.exists(CLIENT_FILE):
    try:
        with open(CLIENT_FILE, 'r') as f:
            purchases = json.load(f)
    except Exception:
        purchases = []
else:
    purchases = []

@app.route('/holiday', methods=['GET'])
def get_destinations():
    db = get_db_connection()
    if not db:
        return jsonify({"message": "Database connection failed"}), 500

    try:
        cursor = db.cursor(dictionary=True)
        # Use IFNULL to avoid NULL issues in features column
        query = """
            SELECT id, destination, price, kind 
            FROM holidays_2025 
            WHERE available = TRUE
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(results), 200
    except Exception as e:
        print(f"[ERROR] Exception in /holiday GET: {e}")
        return jsonify({"message": f"Database error: {str(e)}"}), 500

@app.route('/holiday', methods=['POST'])
def register_client():
    data = request.get_json()
    required_fields = ['id', 'name', 'email', 'kind']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'issue': 'Missing required fields'}), 400

    if any(client['id'] == data['id'] for client in purchases):
        return jsonify({'issue': 'Client already bought a holiday from Travelling with Tavi'}), 200

    if 'destination' not in data or not data['destination']:
        data['destination'] = 'Santorini'

    purchases.append(data)
    try:
        with open(CLIENT_FILE, 'w') as f:
            json.dump(purchases, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to save client data: {e}")

    try:
        send_email(
            to_email=data.get('email'),
            subject="Your Travel Offer from Tavi!",
            name=data.get('name'),
            destination=data.get('destination'),
            kind=data.get('kind'),
            sender_email=os.getenv('SENDER_EMAIL'),
            sender_password=os.getenv('SENDER_PASSWORD')
        )
    except Exception as e:
        print(f"[ERROR] Email sending failed: {e}")

    return jsonify({'message': 'New client added successfully'}), 201

@app.route('/clients', methods=['GET'])
def get_clients():
    return jsonify(purchases), 200

@app.route('/booking', methods=['POST'])
def book_destination():
    data = request.get_json()
    required_fields = ['destinationId', 'email']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing destinationId or email'}), 400

    destination_id = data['destinationId']
    email = data['email']

    db = get_db_connection()
    if not db:
        return jsonify({'message': 'Database connection failed'}), 500

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT destination, kind FROM holidays_2025 WHERE id = %s AND available = TRUE", 
            (destination_id,)
        )
        destination = cursor.fetchone()
        cursor.close()
        db.close()

        if not destination:
            return jsonify({'message': 'Destination not found or unavailable'}), 404

        try:
            send_email(
                to_email=email,
                subject="Your Booking Confirmation",
                name="Valued Customer",
                destination=destination['destination'],
                kind=destination['kind'],
                sender_email=os.getenv('SENDER_EMAIL'),
                sender_password=os.getenv('SENDER_PASSWORD')
            )
        except Exception as e:
            print(f"[ERROR] Email sending failed: {e}")

        return jsonify({'message': 'Booking successful!'}), 200
    except Exception as e:
        print(f"[ERROR] Exception in /booking POST: {e}")
        return jsonify({'message': f'Database error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
