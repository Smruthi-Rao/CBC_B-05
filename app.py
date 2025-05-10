# app.py
from flask import Flask, render_template, jsonify, request
from modules import shared_state
from modules.voice_assistant import chat_with_gpt
from modules.weather_util import get_weather, get_city_from_ip
from modules.outfit_memory import save_history, get_recent_outfits, capture_outfit_snapshot

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/suggest', methods=['GET'])
def suggest_outfit():
    city = get_city_from_ip()
    weather = get_weather(city)
    emotion = shared_state.current_emotion or "neutral"

    prompt = (
        f"You are a fashion assistant. The user is feeling {emotion}. "
        f"The weather in {city} is {weather}. Suggest an outfit."
    )

    outfit = chat_with_gpt(prompt, emotion)
    save_history(outfit)
    return jsonify({"message": outfit})

@app.route('/weather', methods=['GET'])
def get_weather_info():
    city = get_city_from_ip()
    weather = get_weather(city)
    return jsonify({"message": f"The weather in {city} is {weather}."})

@app.route('/save', methods=['POST'])
def save_outfit():
    image_path = capture_outfit_snapshot()
    if image_path:
        name = request.json.get("name", "Unnamed Outfit")
        save_history(name, image_path)
        return jsonify({"message": f"Saved outfit: {name}"})
    return jsonify({"message": "Failed to capture outfit."})

@app.route('/history', methods=['GET'])
def get_outfit_history():
    history = get_recent_outfits()
    return jsonify({"message": "\n".join(history)})

if __name__ == '__main__':
    app.run(debug=True)
