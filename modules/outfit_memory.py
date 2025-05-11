import os
import json
from datetime import datetime
import cv2
import logging
from .database import get_db, save_outfit, get_outfits

# Configure logging
logger = logging.getLogger(__name__)

# Create outfits directory if it doesn't exist
OUTFITS_DIR = "outfits"
if not os.path.exists(OUTFITS_DIR):
    os.makedirs(OUTFITS_DIR)

def capture_outfit_snapshot():
    """Capture an image of the current outfit using webcam"""
    try:
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("Failed to open webcam")
            return None

        # Capture frame
        ret, frame = cap.read()
        cap.release()

        if not ret:
            logger.error("Failed to capture frame")
            return None

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outfit_{timestamp}.jpg"
        filepath = os.path.join(OUTFITS_DIR, filename)

        # Save image
        cv2.imwrite(filepath, frame)
        logger.info(f"Captured outfit snapshot: {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"Error capturing outfit snapshot: {str(e)}")
        return None

def save_history(outfit_description, image_path=None, weather=None, emotion=None):
    """Save outfit information to the database"""
    try:
        # Get database session
        db = next(get_db())
        
        # Save to database
        outfit = save_outfit(
            db=db,
            name=f"Outfit {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            description=outfit_description,
            image_path=image_path,
            weather=weather,
            emotion=emotion
        )
        
        logger.info(f"Saved outfit to database: {outfit.name}")
        return outfit

    except Exception as e:
        logger.error(f"Error saving outfit history: {str(e)}")
        raise

def get_recent_outfits(limit=10):
    """Get recent outfits from the database"""
    try:
        # Get database session
        db = next(get_db())
        
        # Get outfits from database
        outfits = get_outfits(db, limit=limit)
        
        # Format outfit information
        formatted_outfits = []
        for outfit in outfits:
            formatted_outfit = f"Outfit: {outfit['name']}\n"
            if outfit['description']:
                formatted_outfit += f"Description: {outfit['description']}\n"
            if outfit['weather']:
                formatted_outfit += f"Weather: {outfit['weather']}\n"
            if outfit['emotion']:
                formatted_outfit += f"Emotion: {outfit['emotion']}\n"
            formatted_outfit += f"Created: {outfit['created_at']}\n"
            formatted_outfits.append(formatted_outfit)
        
        return formatted_outfits

    except Exception as e:
        logger.error(f"Error getting recent outfits: {str(e)}")
        raise

def is_recently_used(name):
    if not os.path.exists(HISTORY_FILE):
        return False

    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)

    one_week_ago = datetime.now() - timedelta(days=7)

    for entry in reversed(history):
        entry_date = datetime.strptime(entry["date"], "%Y-%m-%d")
        if entry["name"].lower() == name.lower() and entry_date > one_week_ago:
            return True

    return False

def get_recent_outfits():
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)

    return [
        f"{entry['date']}: {entry['name']}"
        for entry in reversed(history)
    ]

def show_last_outfit():
    if not os.path.exists(HISTORY_FILE):
        print("⚠️ No outfit history yet.")
        return

    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)

    if not history:
        print("⚠️ Outfit history is empty.")
        return

    last_entry = history[-1]
    image_path = last_entry.get("image")

    if not image_path or not os.path.exists(image_path):
        print("⚠️ Outfit image not found.")
        return

    image = cv2.imread(image_path)
    window_title = f"Last Outfit: {last_entry['name']} ({last_entry['date']})"
    cv2.imshow(window_title, image)
    print(f"📸 Displaying: {window_title}")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
