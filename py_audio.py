import speech_recognition as sr
import pyttsx3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def speak(audio):
    engine = pyttsx3.init()
    engine.say(audio)
    engine.runAndWait()

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception:
        print("Say that again please...")
        return "None"
    return query

def search_youtube(video):
    speak("Opening YouTube")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(f"https://www.youtube.com/results?search_query={video}")
    time.sleep(5)

if __name__ == "__main__":
    speak("What do you want me to search on YouTube?")
    query = takeCommand().lower()
    search_youtube(query)


# assist=music()
# assist.play("abhi sans lene ki")