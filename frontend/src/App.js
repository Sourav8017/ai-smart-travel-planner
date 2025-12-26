import React, { useState } from "react";
import "./App.css";

function App() {
  const [destination, setDestination] = useState("");
  const [budget, setBudget] = useState("");
  const [days, setDays] = useState("");
  const [travelType, setTravelType] = useState("");
  const [plan, setPlan] = useState("");
  const [confidence, setConfidence] = useState("");
  const [loading, setLoading] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState(false);

  const generatePlan = async () => {
    setLoading(true);
    setPlan("");
    setConfidence("");
    setFeedbackSent(false);

    try {
      const response = await fetch("http://127.0.0.1:5000/generate-plan", {
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
    } catch (error) {
      alert("Backend not reachable");
    } finally {
      setLoading(false);
    }
  };

  const sendFeedback = async (value) => {
    await fetch("http://127.0.0.1:5000/feedback", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        destination,
        budget,
        days,
        travel_type: travelType,
        plan,
        confidence,
        feedback: value,
      }),
    });

    setFeedbackSent(true);
  };

  return (
    <div className="App">
      <h1>AI Smart Travel Planner 🌍</h1>

      <input
        type="text"
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
        <option value="adventure">Adventure</option>
        <option value="leisure">Leisure</option>
        <option value="family">Family</option>
      </select>

      <button onClick={generatePlan} disabled={loading}>
        {loading ? "Generating..." : "Generate Plan"}
      </button>

      {plan && (
        <div className="result">
          <h3>Your Travel Plan</h3>
          <p>{plan}</p>
          <p><strong>Confidence:</strong> {confidence}</p>

          {!feedbackSent ? (
            <div>
              <p>Was this helpful?</p>
              <button onClick={() => sendFeedback("positive")}>👍 Yes</button>
              <button onClick={() => sendFeedback("negative")}>👎 No</button>
            </div>
          ) : (
            <p>✅ Feedback submitted. Thank you!</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
