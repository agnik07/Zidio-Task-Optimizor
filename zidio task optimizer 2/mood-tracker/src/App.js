import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [moods, setMoods] = useState([]);
  const [emotion, setEmotion] = useState("");
  const [userId, setUserId] = useState("");

  // Fetch moods on component mount
  useEffect(() => {
    fetchMoods();
  }, []);

  const fetchMoods = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5001/get_moods");
      setMoods(response.data);
    } catch (error) {
      console.error("Error fetching moods:", error);
    }
  };

  // Log Mood
  const logMood = async () => {
    if (!userId || !emotion) {
      alert("Please enter both User ID and Mood!");
      return;
    }

    try {
      const response = await axios.post("http://127.0.0.1:5001/log_mood", {
        user_id: userId,
        emotion: emotion
      });
      alert(response.data.message);
      setEmotion(""); // Clear input
      fetchMoods(); // Refresh mood list
    } catch (error) {
      console.error("Error logging mood:", error);
      alert("Failed to log mood. Please try again.");
    }
  };

  return (
    <div>
      <h1>Mood Tracker</h1>

      <input
        type="text"
        placeholder="User ID"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
      />
      <input
        type="text"
        placeholder="Enter your mood"
        value={emotion}
        onChange={(e) => setEmotion(e.target.value)}
      />
      <button onClick={logMood}>Log Mood</button>

      <h2>Previous Moods</h2>
      <ul>
        {moods.length > 0 ? (
          moods.map((mood, index) => (
            <li key={index}>{mood.employee_id} - {mood.mood}</li>
          ))
        ) : (
          <p>No moods logged yet.</p>
        )}
      </ul>
    </div>
  );
}

export default App;