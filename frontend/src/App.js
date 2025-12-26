import React, { useState } from "react";
import "./App.css";

const BACKEND_URL = "http://127.0.0.1:5000";

function App() {
  const [destination, setDestination] = useState("");
  const [budget, setBudget] = useState("");
  const [days, setDays] = useState("");
  const [travelType, setTravelType] = useState("");

  const [plan, setPlan] = useState("");
  const [confidence, setConfidence] = useState("");
  const [tripId, setTripId] = useState(null);

  const [rating, setRating] = useState(3);
  const [comment, setComment] = useState("");
  const [feedbackSent, setFeedbackSent] = useState(false);

  const generatePlan = async () => {
    setPlan("");
    setConfidence("");
    setFeedbackSent(false);

    const response = await fetch(`${BACKEND_URL}/generate-plan`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        destination,
        budget,
        days,
        travel_type: travelType,
      }),
    });

    const data = await response.json();
    setPlan(data.plan);
    setConfidence(data.confidence);
    setTripId(data.trip_id);
  };

  const sendFeedback = async (likedValue) => {
    await fetch(`${BACKEND_URL}/feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        trip_id: tripId,
        rating: rating,
        liked: likedValue,
        comment: comment,
      }),
    });

    setFeedbackSent(true);
  };

  return (
    <div className="App">
      <h1>AI Smart Travel Planner 🌍</h1>

      <input
        placeholder="Destination"
        value={destination}
        onChange={(e) => setDestination(e.target.value)}
      />

      <input
        type="number"
        placeholder="Budget"
        value={budget}
        onChange={(e) => setBudget(e.target.value)}
      />

      <input
        type="number"
        placeholder="Days"
        value={days}
        onChange={(e) => setDays(e.target.value)}
      />

      <select value={travelType} onChange={(e) => setTravelType(e.target.value)}>
        <option value="">Select Travel Type</option>
        <option value="leisure">Leisure</option>
        <option value="adventure">Adventure</option>
        <option value="family">Family</option>
      </select>

      <button onClick={generatePlan}>Generate Plan</button>

      {plan && (
        <div className="result">
          <h3>Your Plan</h3>
          <p>{plan}</p>
          <p><strong>Confidence:</strong> {confidence}</p>

          {!feedbackSent ? (
            <>
              <h4>Rate this plan (1–5)</h4>
              <input
                type="range"
                min="1"
                max="5"
                value={rating}
                onChange={(e) => setRating(Number(e.target.value))}
              />
              <p>Rating: {rating}</p>

              <textarea
                placeholder="Optional comment"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
              />

              <div>
                <button onClick={() => sendFeedback(1)}>👍 Like</button>
                <button onClick={() => sendFeedback(0)}>👎 Dislike</button>
              </div>
            </>
          ) : (
            <p>✅ Feedback submitted. Thank you!</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
