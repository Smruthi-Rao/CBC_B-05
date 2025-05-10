import cv2
from deepface import DeepFace
from modules import shared_state
from modules.voice_assistant import chat_with_gpt, speak
import time

def detect_emotion_from_frame():
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Webcam not accessible")
        return

    print("🔍 Emotion detection started... Press 'q' to quit")

    last_emotion = ""
    last_spoken_time = 0
    cooldown_seconds = 30

    while True:
        ret, frame = cam.read()
        if not ret:
            print("⚠️ Failed to read from webcam")
            break

        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            emotion = result[0]['dominant_emotion']
            if emotion != last_emotion:
                current_time = time.time()
                if (current_time - last_spoken_time > cooldown_seconds):
                    last_emotion = emotion
                    shared_state.current_emotion = emotion
                    last_spoken_time = current_time
                    print(f"🧠 Detected Emotion: {emotion}")
                    response = chat_with_gpt("", emotion)
                    speak(response)
        except Exception as e:
            print("Emotion detection error:", e)

        try:
            cv2.putText(frame, shared_state.latest_response, (20, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        except:
            pass

        cv2.imshow("Smart Mirror", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

def detect_initial_emotion():
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Webcam not accessible")
        return "neutral"

    ret, frame = cam.read()
    cam.release()

    if not ret:
        print("⚠️ Failed to capture initial frame")
        return "neutral"

    try:
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        emotion = result[0]['dominant_emotion']
        print(f"🧠 Initial Emotion Detected: {emotion}")
        return emotion
    except Exception as e:
        print("Initial emotion detection error:", e)
        return "neutral"
def show_webcam_with_subtitles():
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Webcam not accessible")
        return

    print("📷 Showing webcam... Press 'q' to quit")

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        # Draw latest ChatGPT reply as subtitle
        try:
            cv2.putText(frame, shared_state.latest_response, (20, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        except:
            pass

        cv2.imshow("Smart Mirror", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
