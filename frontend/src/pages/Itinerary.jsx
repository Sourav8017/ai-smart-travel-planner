import { useState } from "react";
import axios from "axios";
import Feedback from "../components/Feedback";

const API_URL = process.env.REACT_APP_API_URL;

const Itinerary = () => {
  const [destination, setDestination] = useState("");
  const [days, setDays] = useState(3);
  const [interests, setInterests] = useState("");
  const [itinerary, setItinerary] = useState([]);
  const [tripId, setTripId] = useState(null);

  const generateItinerary = async () => {
    try {
      const res = await axios.post(`${API_URL}/generate-itinerary`, {
        user_id: 1,
        destination,
        days,
        interests: interests.split(",").map(i => i.trim())
      });

      setItinerary(res.data.itinerary);
      setTripId(res.data.trip_id);
    } catch (err) {
      console.error(err);
      alert("Failed to generate itinerary");
    }
  };

  return (
    <div>
      <h1>AI Smart Travel Planner</h1>

      <input
        placeholder="Destination"
        value={destination}
        onChange={(e) => setDestination(e.target.value)}
      />

      <input
        type="number"
        value={days}
        onChange={(e) => setDays(e.target.value)}
      />

      <input
        placeholder="Interests (food, beach)"
        value={interests}
        onChange={(e) => setInterests(e.target.value)}
      />

      <button onClick={generateItinerary}>Generate</button>

      {itinerary.length > 0 && (
        <>
          <h2>Your Itinerary</h2>
          {itinerary.map((d) => (
            <div key={d.day}>
              <p>Day {d.day}</p>
              <p>{d.morning}</p>
              <p>{d.afternoon}</p>
              <p>{d.evening}</p>
            </div>
          ))}

          <Feedback tripId={tripId} />
        </>
      )}
    </div>
  );
};

export default Itinerary;
