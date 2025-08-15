import requests
import pyttsx3
import ss  # Loads WEATHER_API_KEY from .env

def speak(audio):
    engine = pyttsx3.init()
    engine.say(audio)
    engine.runAndWait()

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={ss.WEATHER_API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("cod") != 200:
            speak(f"Sorry, I could not find weather information for {city}.")
            return

        main = data.get("main", {})
        temperature_kelvin = main.get("temp")
        humidity = main.get("humidity")
        weather_desc = data.get("weather", [{}])[0].get("description", "")

        if temperature_kelvin is not None:
            temperature_celsius = round(temperature_kelvin - 273.15, 2)
            speak(f"The temperature in {city} is {temperature_celsius} degrees Celsius.")
            print(f"Temperature: {temperature_celsius}°C")
        else:
            speak("Temperature data is not available.")

        if humidity is not None:
            print(f"Humidity: {humidity}%")
        if weather_desc:
            print(f"Weather: {weather_desc}")

    except requests.RequestException as e:
        print("Error fetching weather:", e)
        speak("Sorry, I could not fetch the weather right now.")

if __name__ == "__main__":
    city = input("Enter city name: ")
    get_weather(city)
