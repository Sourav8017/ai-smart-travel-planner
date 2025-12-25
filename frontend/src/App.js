import { useState } from "react";

function App() {
  const [destination, setDestination] = useState("");
  const [budget, setBudget] = useState("");
  const [plan, setPlan] = useState(null);

  const [rating, setRating] = useState(5);
  const [liked, setLiked] = useState(true);
  const [comment, setComment] = useState("");

  const getPlan = async () => {
    const response = await fetch("https://ai-smart-travel-backend.onrender.com/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        destination,
        budget,
        interests: ["nature", "food"]
      })
    });

    const data = await response.json();
    setPlan(data);
  };

  const submitFeedback = async () => {
    await fetch("https://ai-smart-travel-backend.onrender.com/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        trip_id: plan.trip_id,
        rating,
        liked,
        comment
      })
    });

    alert("Feedback submitted successfully ✅");
  };

  return (
    <div style={{ padding: "40px", maxWidth: "600px", fontFamily: "Arial" }}>
      <h1>AI Smart Travel Planner 🌍</h1>

      <input
        placeholder="Destination"
        value={destination}
        onChange={(e) => setDestination(e.target.value)}
        style={{ width: "100%", padding: "8px" }}
      />
      <br /><br />

      <input
        placeholder="Budget"
        value={budget}
        onChange={(e) => setBudget(e.target.value)}
        style={{ width: "100%", padding: "8px" }}
      />
      <br /><br />

      <button onClick={getPlan} style={{ padding: "10px 20px" }}>
        Generate Plan
      </button>

      {plan && (
        <div style={{ marginTop: "30px" }}>
          <h3>Trip Itinerary</h3>

          <p>
            <strong>Recommendation Confidence:</strong>{" "}
            {plan.confidence}
          </p>

          <p style={{ color: "#555" }}>
            <em>{plan.explanation}</em>
          </p>

          <ul>
            {plan.itinerary.map((day, index) => (
              <li key={index}>{day}</li>
            ))}
          </ul>

          <hr />

          <h3>Give Feedback</h3>

          <label>Rating (1–5)</label><br />
          <input
            type="number"
            min="1"
            max="5"
            value={rating}
            onChange={(e) => setRating(e.target.value)}
          />
          <br /><br />

          <label>
            <input
              type="checkbox"
              checked={liked}
              onChange={() => setLiked(!liked)}
            />{" "}
            I liked this plan
          </label>
          <br /><br />

          <textarea
            placeholder="Your feedback"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            style={{ width: "100%", padding: "8px" }}
          />
          <br /><br />

          <button onClick={submitFeedback}>
            Submit Feedback
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
