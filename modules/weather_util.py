import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENWEATHER_API_KEY")

def get_city_from_ip():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        return data.get("city", "Bangalore")
    except:
        return "Bangalore"  # fallback

def get_weather(city_name):
    if not api_key:
        return "weather API key missing"

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            print("⚠️ Weather API error:", data.get("message"))
            return "weather unavailable"

        weather_desc = data["weather"][0]["main"].lower()
        temperature = round(data["main"]["temp"])
        return f"{weather_desc}, {temperature}°C"
    except Exception as e:
        print("Weather fetch error:", e)
        return "weather unavailable"
