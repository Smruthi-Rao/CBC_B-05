import cv2
from deepface import DeepFace
from modules import shared_state

def detect_emotion_from_frame():
    cam = cv2.VideoCapture(0)
    print("🔍 Emotion detection started...")

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            emotion = result[0]['dominant_emotion']
            shared_state.current_emotion = emotion
            #print("🧠 Detected Emotion:", emotion)

            cv2.putText(frame, f"Emotion: {emotion}", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        except Exception as e:
            print("Error:", e)

        cv2.imshow("SmartMirror AI - Webcam", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Optional manual kill
            break

    cam.release()
    cv2.destroyAllWindows()
