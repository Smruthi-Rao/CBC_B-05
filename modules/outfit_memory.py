import os
import json
import cv2
import uuid
from datetime import datetime, timedelta

HISTORY_FILE = "outfit_history.json"
OUTFIT_DIR = "outfits/"

# Create outfit directory if it doesn't exist
os.makedirs(OUTFIT_DIR, exist_ok=True)

def save_history(name, image_path=None):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)

    history.append({
        "name": name,
        "image": image_path,
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

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

def capture_outfit_snapshot():
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Webcam not accessible")
        return None

    ret, frame = cam.read()
    cam.release()

    if not ret:
        print("⚠️ Could not read frame.")
        return None

    filename = os.path.join(OUTFIT_DIR, f"{uuid.uuid4().hex}.jpg")
    cv2.imwrite(filename, frame)
    return filename

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
