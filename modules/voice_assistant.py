import os
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import openai
from modules import shared_state
from modules.weather_util import get_weather

stop_speaking = False

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

engine = pyttsx3.init()
engine.setProperty('rate', 170)       # Set normal speaking rate
engine.setProperty('volume', 1.0)     # Max volume

def speak(text):
    global stop_speaking
    stop_speaking = False
    print("🪞 Mirror says:", text)

    try:
        engine.stop()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("❌ TTS error:", e)

    shared_state.latest_response = text


def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
        except sr.WaitTimeoutError:
            print("⚠️ Listening timed out.")
            return ""

    try:
        text = recognizer.recognize_google(audio)
        print("👤 You said:", text)
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return ""
    except sr.RequestError:
        print("❌ Speech service down")
        return ""


def chat_with_gpt(user_input, emotion="neutral"):
    prompt = f"""
    You are a smart, silly, sarcastic best friend.
    Your user is feeling {emotion}.
    User said: {user_input}
    Reply like a friend, not a therapist. Be witty or savage if needed.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            max_tokens=100,
            temperature=0.8
        )
        reply = response['choices'][0]['message']['content'].strip()
        shared_state.latest_response = reply
        return reply
    except Exception as e:
        print("OpenAI Error:", e)
        shared_state.latest_response = "I’m having a dumb moment. Try again."
        return "I’m having a dumb moment. Try again."


def run_friend_chat(paused):
    global stop_speaking

    user_input = listen()
    if not user_input:
        return True, None

    user_input_lower = user_input.lower()

    if "stop" in user_input_lower:
        stop_speaking = True
        engine.stop()
        return True, None

    if paused and user_input_lower.startswith("hey sakha"):
        speak("I knew you'd come back. What now?")
        return True, "resume"

    if paused:
        return True, None

    if "stop talking" in user_input_lower or "shut up" in user_input_lower:
        speak("Fine! I’m muting myself. Say 'Hey Sakha' if you miss me.")
        return True, "pause"

    if any(p in user_input_lower for p in ["bye", "goodnight", "see you"]):
        speak("Sleep well, drama queen.")
        return False, None

    if "what should i wear" in user_input_lower or "suggest outfit" in user_input_lower:
        city = "Bangalore"
        weather = get_weather(city)
        emotion = shared_state.current_emotion

        prompt = (
            f"You are a smart fashion assistant. The user is feeling {emotion} "
            f"and the weather in {city} is {weather}. Suggest a casual outfit "
            f"that suits both their mood and the weather."
        )

        outfit = chat_with_gpt(prompt, emotion)
        speak(outfit)
        return True, None

    emotion = shared_state.current_emotion
    reply = chat_with_gpt(user_input_lower, emotion)
    speak(reply)
    return True, None
