from modules.emotion_detector import detect_initial_emotion, show_webcam_with_subtitles
from modules.voice_assistant import run_friend_chat, speak
from modules import shared_state
import threading

# 🧠 One-time emotion detection
initial_emotion = detect_initial_emotion()
shared_state.current_emotion = initial_emotion
speak(f"You look {initial_emotion} today! Want to talk or need a suggestion?")

# ✅ Just show webcam with subtitles — no repeated emotion detection
threading.Thread(target=show_webcam_with_subtitles, daemon=True).start()

# 🎤 Voice assistant loop
paused = False
while True:
    should_continue, pause_toggle = run_friend_chat(paused)

    if pause_toggle == "pause":
        paused = True
        continue
    if pause_toggle == "resume":
        paused = False
        continue
    if not should_continue:
        break
