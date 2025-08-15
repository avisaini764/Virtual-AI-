import requests
import pyttsx3
import ss  # Loads keys from .env

def speak(audio):
    engine = pyttsx3.init()
    engine.say(audio)
    engine.runAndWait()

def get_news():
    url = f"https://newsdata.io/api/1/news?apikey={ss.NEWS_API_KEY}&country=in&language=en"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            speak("Sorry, I could not find any news right now.")
            return

        articles = data["results"]

        for idx, article in enumerate(articles[:10], start=1):
            title = article.get("title", "No title available")
            print(f"{idx}. {title}")
            speak(title)

    except requests.RequestException as e:
        print("Error fetching news:", e)
        speak("Sorry, I could not fetch the news right now.")

if __name__ == "__main__":
    get_news()
