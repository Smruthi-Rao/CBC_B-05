import threading
from modules.emotion_detector import detect_emotion_from_frame
from modules.voice_assistant import run_friend_chat

# Start webcam in background
emotion_thread = threading.Thread(target=detect_emotion_from_frame)
emotion_thread.daemon = True
emotion_thread.start()

# Loop: voice + chat
while True:
    should_continue = run_friend_chat()
    if not should_continue:
        break
