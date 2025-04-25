react.js
import React, { useState, useEffect } from "react";

function App() {
  const [moods, setMoods] = useState([]);
  const [emotion, setEmotion] = useState("");
  const [userId, setUserId] = useState("");

  // Fetch moods from Flask
  useEffect(() => {
    fetch("http://127.0.0.1:5001/get_moods")
      .then((response) => response.json())
      .then((data) => setMoods(data))
      .catch((error) => console.error("Error fetching moods:", error));
  }, []);

  // Function to log mood
  const logMood = async () => {
    const response = await fetch("http://127.0.0.1:5001/log_mood", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, emotion }),
    });

    const data = await response.json();
    alert(data.message);
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
        {moods.map((mood, index) => (
          <li key={index}>{mood[1]} - {mood[3]}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;