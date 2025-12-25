from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db
from models import Trip, Feedback
from sqlalchemy import func
import os
import subprocess
import sys

# Safe ML import
try:
    from ml.predict import predict_score
except:
    predict_score = None

app = Flask(__name__)

# 🔥 FINAL CORS FIX (Render + Vercel safe)
CORS(app)

# Force CORS headers on ALL responses (including OPTIONS)
@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///travel.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return {"message": "AI Smart Travel Planner Backend Running 🚀"}

# -------------------------------------------------
# EXPLAINABLE AI LOGIC
# -------------------------------------------------
def generate_explanation(interests, confidence):
    if confidence == "baseline":
        return "Recommendation based on general travel popularity."

    reasons = []

    if "nature" in interests:
        reasons.append("you prefer nature-based trips")

    if "food" in interests:
        reasons.append("you enjoy food experiences")

    reasons.append("similar trips received positive feedback")

    return "Recommended because " + " and ".join(reasons) + "."

# -------------------------------------------------
# AUTO-RETRAIN CHECK
# -------------------------------------------------
def should_retrain_model(threshold=5):
    count = db.session.query(func.count(Feedback.id)).scalar()
    return count % threshold == 0

# -------------------------------------------------
# CREATE TRAVEL PLAN
# -------------------------------------------------
@app.route("/plan", methods=["POST", "OPTIONS"])
def create_plan():
    if request.method == "OPTIONS":
        return "", 200

    data = request.json

    trip = Trip(
        destination=data.get("destination"),
        budget=data.get("budget"),
        interests=",".join(data.get("interests", []))
    )

    db.session.add(trip)
    db.session.commit()

    confidence = "baseline"

    model_path = "ml/travel_model.pkl"
    if os.path.exists(model_path) and predict_score:
        try:
            confidence = predict_score(5)
        except:
            confidence = "baseline"

    explanation = generate_explanation(
        data.get("interests", []),
        confidence
    )

    return jsonify({
        "trip_id": trip.id,
        "confidence": confidence,
        "explanation": explanation,
        "itinerary": [
            "Day 1: Local sightseeing",
            "Day 2: Explore popular attractions",
            "Day 3: Relax and return"
        ]
    })

# -------------------------------------------------
# SAVE FEEDBACK + AUTO RETRAIN
# -------------------------------------------------
@app.route("/feedback", methods=["POST", "OPTIONS"])
def save_feedback():
    if request.method == "OPTIONS":
        return "", 200

    data = request.json

    feedback = Feedback(
        trip_id=data.get("trip_id"),
        rating=int(data.get("rating")),
        liked=bool(data.get("liked")),
        comment=data.get("comment")
    )

    db.session.add(feedback)
    db.session.commit()

    retrain_status = "Waiting for more feedback"

    if should_retrain_model():
        try:
            subprocess.run(
                [sys.executable, "ml/train_model.py"],
                check=True
            )
            retrain_status = "Model retrained successfully"
        except:
            retrain_status = "Model retraining failed"

    return {
        "message": "Feedback saved successfully ✅",
        "retrain_status": retrain_status
    }

if __name__ == "__main__":
    app.run(debug=True)
