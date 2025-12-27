🧠 AI Smart Travel Planner
A full-stack AI-inspired travel planning system that generates personalized itineraries and learns from user feedback over time.
The project demonstrates real-world backend engineering, frontend integration, and recommendation system fundamentals—with graceful handling of AI limitations.

🚀 Features
🌍 Generate multi-day travel itineraries based on destination & interests

⭐ User feedback system (rating, like/dislike, comments)

🧠 Feedback-driven learning & personalization

🔁 Preference-based recommendation logic

⚙️ Graceful fallback when AI services are unavailable

🌐 Frontend–backend integration with CORS & env-based config

🧪 ML-ready database schema for future enhancements

🏗️ Tech Stack
Frontend
React

React Router

Axios

CSS

Backend
Python (Flask)

SQLite

Flask-CORS

Concepts Used
REST APIs

Content-based recommendation systems

Feedback loops

Preference weighting

Environment-based configuration

Git & GitHub workflows

📂 Project Structure
bash
Copy code
ai-smart-travel-planner/
│
├── backend/
│   ├── app.py                # Main Flask app
│   ├── init_db.py            # DB initialization
│   ├── database.py
│   ├── models.py
│   ├── seed_db.py
│   ├── seed_feedback.py
│   └── instance/
│       └── travel.db         # SQLite database
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Feedback.jsx  # ⭐ Rating & feedback UI
│   │   ├── pages/
│   │   │   └── Itinerary.jsx # Itinerary page
│   │   ├── App.js
│   │   └── index.js
│   └── .env                  # API URL (ignored by git)
│
└── README.md
⚙️ How the System Works
1️⃣ Itinerary Generation
User enters destination, days, and interests

Backend generates an itinerary using:

Preference-based logic

Rule-based fallback (if AI quota is unavailable)

2️⃣ Feedback Collection
User rates the itinerary (⭐ 1–5)

Like / dislike + optional comment

Feedback is sent to /feedback endpoint

3️⃣ Learning & Personalization
Feedback updates interest weights in the database

Future itineraries prioritize high-rated interests

This forms a content-based recommendation loop

📌 Even without paid AI APIs, the system learns and adapts.

🧠 Recommendation Logic (Simplified)
text
Copy code
User likes "food" trips →
Food interest weight increases →
Next itinerary prioritizes food activities
This mirrors how real systems (Netflix, Spotify, travel apps) work at a basic level.

🧪 API Endpoints
Generate Itinerary
bash
Copy code
POST /generate-itinerary
Request

json
Copy code
{
  "user_id": 1,
  "destination": "Goa",
  "days": 3,
  "interests": ["food", "beach"]
}
Submit Feedback
bash
Copy code
POST /feedback
Request

json
Copy code
{
  "trip_id": 5,
  "user_id": 1,
  "rating": 5,
  "liked": 1,
  "comment": "Loved the food spots"
}
▶️ How to Run Locally
Backend
bash
Copy code
cd backend
python app.py
Runs on:

cpp
Copy code
http://127.0.0.1:5000
Frontend
bash
Copy code
cd frontend
npm install
npm start
Runs on:

arduino
Copy code
http://localhost:3000
Environment Variable (Frontend)
Create frontend/.env:

env
Copy code
REACT_APP_API_URL=http://127.0.0.1:5000
⚠️ .env is ignored by Git for security.

🌐 Deployment Strategy (Explained)
Frontend & backend can be deployed separately

API base URL is configurable via environment variables

AI services are optional; system gracefully falls back

Suitable for budget-constrained deployments

💡 Design Decisions
SQLite chosen for simplicity and portability

Feedback-driven learning instead of black-box AI

Modular frontend components

Clean REST API boundaries

Production-style Git workflow (no force pushes)

🧑‍💻 What This Project Demonstrates
Full-stack development skills

Backend API design

Recommendation system fundamentals

Handling third-party service limitations

Clean Git & GitHub usage

Realistic engineering trade-offs

📌 Resume-Ready Description
Built a full-stack AI-inspired travel planner with feedback-driven personalization using React and Flask. Implemented content-based recommendation logic, user feedback loops, and preference weighting to adapt itineraries over time, with graceful fallback handling for AI service limitations.

📜 License
This project is for educational and demonstration purposes.