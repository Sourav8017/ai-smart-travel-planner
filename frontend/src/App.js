import React, { useState } from "react";
import "./App.css";

function App() {
  const [budget, setBudget] = useState("");
  const [days, setDays] = useState("");
  const [travelType, setTravelType] = useState("leisure");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [mode, setMode] = useState("");

  const generatePlan = async () => {
    setLoading(true);
    setError("");
    setRecommendations([]);
    setMode("");

    try {
      const response = await fetch("http://127.0.0.1:5000/generate-plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          budget: Number(budget),
          days: Number(days),
          travel_type: travelType
        })
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.message || "Failed to generate plan");
      } else {
        setMode(data.mode);
        setRecommendations(
          data.recommendations.map(t => ({
            ...t,
            rating: 5,
            comment: "",
            feedbackSent: false
          }))
        );
      }
    } catch (err) {
      setError("Backend not reachable. Is Flask running?");
    } finally {
      setLoading(false);
    }
  };

  const sendFeedback = async (trip, liked) => {
    await fetch("http://127.0.0.1:5000/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        trip_id: trip.trip_id,
        rating: trip.rating,
        liked: liked,
        comment: trip.comment
      })
    });

    setRecommendations(prev =>
      prev.map(t =>
        t.trip_id === trip.trip_id ? { ...t, feedbackSent: true } : t
      )
    );
  };

  const modeMessage = {
    exact: "✅ Exact matches for your preferences",
    budget_relaxed: "ℹ️ Showing trips with slightly higher budget",
    days_relaxed: "ℹ️ Showing trips with slightly longer duration",
    popular_fallback: "🔥 Popular trips users love"
  };

  return (
    <div className="app-container">
      <h1>AI Smart Travel Planner ✈️</h1>

      <div className="form-box">
        <div className="form-group">
          <label>Budget (₹)</label>
          <input type="number" value={budget} onChange={e => setBudget(e.target.value)} />
        </div>

        <div className="form-group">
          <label>Days</label>
          <input type="number" value={days} onChange={e => setDays(e.target.value)} />
        </div>

        <div className="form-group">
          <label>Travel Type</label>
          <select value={travelType} onChange={e => setTravelType(e.target.value)}>
            <option value="leisure">Leisure</option>
            <option value="adventure">Adventure</option>
          </select>
        </div>

        <button onClick={generatePlan} disabled={loading}>
          {loading ? "Generating..." : "Generate Plan"}
        </button>

        {error && <p className="error">{error}</p>}
      </div>

      {mode && <p style={{ marginBottom: "20px" }}>{modeMessage[mode]}</p>}

      {recommendations.map(trip => {
        const percent = Math.round(trip.like_probability * 100);

        return (
          <div className="trip-card" key={trip.trip_id}>
            <h3>{trip.destination}</h3>
            <p className="trip-meta">
              ₹{trip.budget} • {trip.days} days • {trip.travel_type}
            </p>

            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${percent}%` }} />
            </div>

            {!trip.feedbackSent ? (
              <>
                <button className="like-btn" onClick={() => sendFeedback(trip, 1)}>👍 Like</button>
                <button className="dislike-btn" onClick={() => sendFeedback(trip, 0)}>👎 Dislike</button>
              </>
            ) : (
              <p className="feedback-success">✅ Feedback submitted</p>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default App;
