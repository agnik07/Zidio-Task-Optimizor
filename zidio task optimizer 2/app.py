from flask import Flask, request, jsonify
from flask_cors import CORS
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import cv2
import tensorflow as tf
import speech_recognition as sr
import numpy as np
import dlib
import psycopg2
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow requests from React frontend

# Load AI models
nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()
face_detector = dlib.get_frontal_face_detector()

# Load emotion recognition model (Ensure the model exists)
try:
    model = tf.keras.models.load_model("emotion_model.h5")
except Exception as e:
    print("Error loading model:", e)

# Connect to PostgreSQL Database
conn = psycopg2.connect(
    dbname="mood_db",
    user="mood_user",
    password="0024",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Ensure the table exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS mood_tracking (
        id SERIAL PRIMARY KEY,
        employee_id TEXT NOT NULL,
        mood TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
conn.commit()


# **Text-Based Emotion Analysis**
@app.route("/analyze_text", methods=["POST"])
def analyze_text():
    data = request.json
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "Text is required"}), 400

    sentiment_score = sia.polarity_scores(text)["compound"]
    sentiment = "positive" if sentiment_score > 0 else "negative" if sentiment_score < 0 else "neutral"

    cursor.execute("INSERT INTO mood_tracking (employee_id, mood) VALUES (%s, %s)", ("EMP001", sentiment))
    conn.commit()

    return jsonify({"emotion": sentiment})


# **Speech-Based Emotion Analysis**
@app.route("/analyze_speech", methods=["POST"])
def analyze_speech():
    recognizer = sr.Recognizer()
    file = request.files.get("audio")

    if not file:
        return jsonify({"error": "Audio file is required"}), 400

    with sr.AudioFile(file) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)

        sentiment_score = sia.polarity_scores(text)["compound"]
        sentiment = "positive" if sentiment_score > 0 else "negative" if sentiment_score < 0 else "neutral"

        cursor.execute("INSERT INTO mood_tracking (employee_id, mood) VALUES (%s, %s)", ("EMP001", sentiment))
        conn.commit()

        return jsonify({"emotion": sentiment})


# **Face-Based Emotion Analysis**
@app.route("/analyze_face", methods=["POST"])
def analyze_face():
    file = request.files.get("image")

    if not file:
        return jsonify({"error": "Image file is required"}), 400

    nparr = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    faces = face_detector(img, 1)

    emotion = "neutral" if len(faces) == 0 else "stressed"

    cursor.execute("INSERT INTO mood_tracking (employee_id, mood) VALUES (%s, %s)", ("EMP001", emotion))
    conn.commit()

    return jsonify({"emotion": emotion})


# **Task Recommendation System**
@app.route("/recommend_task", methods=["POST"])
def recommend_task():
    data = request.json
    emotion = data.get("emotion", "neutral")
    
    task_suggestions = {
        "positive": "Creative brainstorming session",
        "negative": "Take a short break",
        "neutral": "Proceed with routine tasks"
    }

    return jsonify({"recommended_task": task_suggestions.get(emotion, "Regular work")})


# **Team Mood Analytics**
@app.route("/team_mood", methods=["GET"])
def team_mood():
    cursor.execute("SELECT mood, COUNT(*) FROM mood_tracking GROUP BY mood;")
    mood_data = cursor.fetchall()

    mood_summary = {mood: count for mood, count in mood_data}
    return jsonify({"team_mood": mood_summary})


# **Historical Mood Tracking**
@app.route("/get_moods", methods=["GET"])
def get_moods():
    cursor.execute("SELECT employee_id, mood FROM mood_tracking ORDER BY timestamp DESC LIMIT 10;")
    history = cursor.fetchall()

    mood_history = [{"employee_id": mood[0], "mood": mood[1]} for mood in history]
    return jsonify(mood_history)


# **Log a Mood**
@app.route("/log_mood", methods=["POST"])
def log_mood():
    data = request.json
    user_id = data.get("user_id", "")
    emotion = data.get("emotion", "")

    if not user_id or not emotion:
        return jsonify({"error": "User ID and mood are required"}), 400

    cursor.execute("INSERT INTO mood_tracking (employee_id, mood) VALUES (%s, %s)", (user_id, emotion))
    conn.commit()

    return jsonify({"message": "Mood logged successfully"})


# **Home Route**
@app.route("/")
def home():
    return "Flask server is running!"


# **Run Flask App**
if __name__ == "__main__":
    app.run(debug=True, port=5001)