# app.py
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Add file handler for logging
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize modules with error handling
try:
    from modules import shared_state
    from modules.voice_assistant import chat_with_gpt
    from modules.weather_util import get_weather, get_city_from_ip
    from modules.outfit_memory import save_history, get_recent_outfits, capture_outfit_snapshot
    MODULES_LOADED = True
except ImportError as e:
    logger.error(f"Failed to load modules: {str(e)}")
    MODULES_LOADED = False

@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler for all routes"""
    error_message = str(error)
    logger.error(f"Error occurred: {error_message}\n{traceback.format_exc()}")
    return jsonify({
        "error": "An unexpected error occurred",
        "message": error_message
    }), 500

@app.route('/')
def home():
    """Render the main page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering home page: {str(e)}")
        raise

@app.route('/suggest', methods=['GET'])
def suggest_outfit():
    """Get outfit suggestion based on weather and emotion"""
    if not MODULES_LOADED:
        return jsonify({
            "error": "Required modules not loaded",
            "message": "Please check the server logs for details"
        }), 500

    try:
        city = get_city_from_ip()
        weather = get_weather(city)
        emotion = shared_state.current_emotion or "neutral"

        logger.info(f"Generating outfit suggestion for city: {city}, weather: {weather}, emotion: {emotion}")

        prompt = (
            f"You are a fashion assistant. The user is feeling {emotion}. "
            f"The weather in {city} is {weather}. Suggest an outfit."
        )

        outfit = chat_with_gpt(prompt, emotion)
        save_history(outfit)
        
        return jsonify({
            "message": outfit,
            "metadata": {
                "city": city,
                "weather": weather,
                "emotion": emotion,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error generating outfit suggestion: {str(e)}")
        return jsonify({
            "error": "Failed to generate outfit suggestion",
            "message": str(e)
        }), 500

@app.route('/weather', methods=['GET'])
def get_weather_info():
    """Get current weather information"""
    if not MODULES_LOADED:
        return jsonify({
            "error": "Required modules not loaded",
            "message": "Please check the server logs for details"
        }), 500

    try:
        city = get_city_from_ip()
        weather = get_weather(city)
        logger.info(f"Retrieved weather for {city}: {weather}")
        
        return jsonify({
            "message": f"The weather in {city} is {weather}.",
            "metadata": {
                "city": city,
                "weather": weather,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error getting weather info: {str(e)}")
        return jsonify({
            "error": "Failed to get weather information",
            "message": str(e)
        }), 500

@app.route('/save', methods=['POST'])
def save_outfit():
    """Save current outfit with optional name"""
    if not MODULES_LOADED:
        return jsonify({
            "error": "Required modules not loaded",
            "message": "Please check the server logs for details"
        }), 500

    try:
        if not request.is_json:
            raise ValueError("Request must be JSON")

        name = request.json.get("name", "Unnamed Outfit")
        image_path = capture_outfit_snapshot()
        
        if not image_path:
            raise ValueError("Failed to capture outfit image")

        save_history(name, image_path)
        logger.info(f"Saved outfit: {name} with image at {image_path}")
        
        return jsonify({
            "message": f"Saved outfit: {name}",
            "metadata": {
                "name": name,
                "image_path": image_path,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error saving outfit: {str(e)}")
        return jsonify({
            "error": "Failed to save outfit",
            "message": str(e)
        }), 500

@app.route('/history', methods=['GET'])
def get_outfit_history():
    """Get recent outfit history"""
    if not MODULES_LOADED:
        return jsonify({
            "error": "Required modules not loaded",
            "message": "Please check the server logs for details"
        }), 500

    try:
        history = get_recent_outfits()
        logger.info(f"Retrieved {len(history)} outfit history entries")
        
        return jsonify({
            "message": "\n".join(history),
            "metadata": {
                "count": len(history),
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error getting outfit history: {str(e)}")
        return jsonify({
            "error": "Failed to get outfit history",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting Smart Mirror application")
    app.run(host='127.0.0.1', port=8080, debug=True)
