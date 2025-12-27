import { useState } from "react";
import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL;

const Feedback = ({ tripId, userId = 1 }) => {
  const [rating, setRating] = useState(0);
  const [liked, setLiked] = useState(null);
  const [comment, setComment] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const submitFeedback = async () => {
    if (rating === 0) {
      alert("Please give a rating");
      return;
    }

    try {
      await axios.post(`${API_URL}/feedback`, {
        trip_id: tripId,
        user_id: userId,
        rating,
        liked: liked ? 1 : 0,
        comment
      });

      setSubmitted(true);
    } catch (err) {
      console.error(err);
      alert("Failed to submit feedback");
    }
  };

  if (submitted) {
    return <p style={{ color: "green" }}>✅ Feedback submitted!</p>;
  }

  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Rate this itinerary</h3>

      {[1, 2, 3, 4, 5].map((n) => (
        <span
          key={n}
          onClick={() => setRating(n)}
          style={{
            fontSize: "24px",
            cursor: "pointer",
            color: rating >= n ? "gold" : "gray"
          }}
        >
          ★
        </span>
      ))}

      <div style={{ marginTop: "10px" }}>
        <button onClick={() => setLiked(true)}>👍 Like</button>
        <button onClick={() => setLiked(false)}>👎 Dislike</button>
      </div>

      <textarea
        placeholder="Optional comment"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        style={{ width: "100%", marginTop: "10px" }}
      />

      <button onClick={submitFeedback} style={{ marginTop: "10px" }}>
        Submit Feedback
      </button>
    </div>
  );
};

export default Feedback;
