from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil import parser
import os

# Step 1: Initialize SQLAlchemy (without app)
db = SQLAlchemy()

# Step 2: Create the Flask app
def create_app():
    app = Flask(__name__)

    # Use DATABASE_URL from environment variable (secure on Render)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Webhook route for Spot AI
    @app.route("/webhook/spotai", methods=["POST"])
    def spotai_webhook():
        data = request.get_json()

        plate = data.get("plate")
        captured_at = data.get("captured_at")

        if not plate:
            return jsonify({"error": "Missing 'plate'"}), 400

        new_record = Cam1(lp=plate)

        if captured_at:
            try:
                new_record.scan_time = parser.isoparse(captured_at)
            except Exception as e:
                return jsonify({"error": "Invalid timestamp format"}), 400

        db.session.add(new_record)
        db.session.commit()

        return jsonify({"message": f"Plate '{plate}' saved."}), 200

    return app

# Step 3: Define the table model
class Cam1(db.Model):
    __tablename__ = 'Cam1'
    id = db.Column(db.Integer, primary_key=True)
    lp = db.Column(db.String(20), nullable=False)
    scan_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Cam1 {self.lp} at {self.scan_time}>"

# Step 4: Run table creation on startup
app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Table 'Cam1' created.")
