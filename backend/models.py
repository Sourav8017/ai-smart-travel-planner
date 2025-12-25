from database import db
from datetime import datetime

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(100))
    budget = db.Column(db.String(50))
    interests = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer)
    rating = db.Column(db.Integer)      # 1–5
    liked = db.Column(db.Boolean)        # true / false
    comment = db.Column(db.String(300))
