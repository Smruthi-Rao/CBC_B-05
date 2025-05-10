import os
import threading
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import openai
from modules import shared_state
from modules.weather_util import get_weather, get_city_from_ip
from modules.outfit_memory import (
    save_history, is_recently_used, get_recent_outfits,
    capture_outfit_snapshot, show_last_outfit
)

stop_speaking = False

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

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
    user_input = listen()
    if not user_input:
        return True, None

    user_input_lower = user_input.lower()

    if paused and "resume" in user_input_lower:
        speak("I knew you'd come back. What now?")
        return True, "resume"

    if paused:
        return True, None

    if "stop talking" in user_input_lower or "shut up" in user_input_lower:
        speak("Fine! I’m muting myself. Say 'resume' if you miss me.")
        return True, "pause"

    if any(p in user_input_lower for p in ["bye", "goodnight", "see you"]):
        speak("Sleep well, drama queen.")
        return False, None

    if "this is my outfit" in user_input_lower or "save my outfit" in user_input_lower:
        speak("Smile! Capturing your fabulous look...")
        image_path = capture_outfit_snapshot()
        if image_path:
            speak("What should I call this outfit?")
            name = listen()
            if name:
                save_history(name, image_path)
                speak(f"Outfit '{name}' saved successfully!")
            else:
                speak("No name given. Outfit not saved.")
        else:
            speak("Could not capture your outfit. Try again.")
        return True, None

    if "what did i wear" in user_input_lower or "past outfits" in user_input_lower:
        recent = get_recent_outfits()
        if not recent:
            speak("No outfit history yet, fashion ghost.")
        else:
            summary = "Here’s what you’ve worn:\n" + "\n".join(recent)
            speak(summary)
        return True, None

    if "show my outfit" in user_input_lower or "show last outfit" in user_input_lower:
        threading.Thread(target=show_last_outfit, daemon=True).start()
        speak("Here’s what you wore last time.")
        return True, None

    if any(x in user_input_lower for x in ["what should i wear", "suggest outfit", "fit to wear", "outfit"]):
        city = get_city_from_ip()
        weather = get_weather(city)
        emotion = shared_state.current_emotion
        prompt = (
            f"You are a smart fashion assistant. The user is feeling {emotion}. "
            f"The weather in {city} is {weather}. "
            f"Suggest a stylish outfit that fits their mood and the current weather. Be witty."
        )
        outfit = chat_with_gpt(prompt, emotion)
        if is_recently_used(outfit):
            speak("We just wore that! Try something new today.")
        else:
            save_history(outfit)
            speak(outfit)
        return True, None

    if "weather" in user_input_lower:
        city = get_city_from_ip()
        weather = get_weather(city)
        speak(f"The weather in {city} is {weather}.")
        return True, None

    emotion = shared_state.current_emotion
    reply = chat_with_gpt(user_input_lower, emotion)
    speak(reply)
    return True, None
