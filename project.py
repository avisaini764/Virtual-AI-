# import pyttsx3 as p
# import speech_recognition as sr
# from selenium_web import *
# from py_audio import *
# from news import *
# import randfacts
# from weather import *
# import datetime
# import webbrowser

# engine =p.init()
# rate =engine.getProperty('rate')
# # print(rate)
# engine.setProperty('rate',120)
# voices=engine.getProperty('voices')
# engine.setProperty('voice',voices[1].id)
# # print(voices)
# # print(rate)
# def speak(text):
#     engine.say(text)
#     engine.runAndWait()

# def wishme():
#     hour=int(datetime.datetime.now().hour)
#     if hour>0 and hour<12:
#         return("Morning")
#     elif hour>12 and hour<16:
#         return("Afternoon")
#     else:
#         return("Evening")

# today_date=datetime.datetime.now()


# r=sr.Recognizer()
# speak(" Hello User!,Good" +wishme()+"I am your voice assistant Siri")
# speak(" Today is"+today_date.strftime(" %d")+"of"+ today_date.strftime(" %B")+ today_date.strftime(" %I")+today_date.strftime(" :%M")+today_date.strftime(" %p")+" And is currently"+ (today_date.strftime(" %Y")))
# print(" Today is"+today_date.strftime(" %d")+"of"+ today_date.strftime(" %B")+ today_date.strftime(" %I")+today_date.strftime(" :%M")+today_date.strftime(" %p")+ " And is currently"+ (today_date.strftime(" %Y")))
# city = "Shimla"
# api_key = "5ea235ce259443ccaee574a606658f4e"
# speak(" Temperature in Shimla is"+ str(temp(city,api_key))+" Degree celcius"+" and with "+str(des(city,api_key)))
# print(" Temperature in Shimla is"+ str(temp(city,api_key))+" Degree celcius"+" and with "+str(des(city,api_key)))
# speak(" How are you?")

# with sr.Microphone() as source:
#     r.energy_threshold=10000
#     r.adjust_for_ambient_noise(source,1.2)
#     print("listening")
#     audio = r.listen(source)
#     text = r.recognize_google(audio)

#     print(text)
# if "what" in text and "about" in text and "you" in text:
#     speak("i am also having a good day mam")

# speak(" what can i do for you??")

# with sr.Microphone() as source:
#     r.energy_threshold=20000
#     r.adjust_for_ambient_noise(source,1.2)
#     print("listening")
#     audio = r.listen(source)
#     text2= r.recognize_google(audio)

# if "information" in text2:
#     speak("you need information to which topic")

#     with sr.Microphone() as source:
#       r.energy_threshold=20000
#       r.adjust_for_ambient_noise(source,1.2)
#       print("listening")
#       audio = r.listen(source)
#       infor= r.recognize_google(audio)
#     speak("i am searching your data mam!".format(infor))
#     print("i am searching your data mam!".format(infor))

#     assist=infow()
#     assist.get_info(infor)

# elif "play" in text2 and "video" in text2:
#     speak("you want to play which video??")
#     print("you want to play which video??")

#     with sr.Microphone() as source:
#       r.energy_threshold=20000
#       r.adjust_for_ambient_noise(source,1.2)
#       print("listening")
#       audio = r.listen(source)
#       vid= r.recognize_google(audio)
#     speak("playing {} on youtube".format(vid))
#     print("playing {} on youtube".format(vid))
#     assist=music()
#     assist.play(vid)
# elif "open facebook" in text2:
#     speak("Opening Facebook")
#     webbrowser.open("https://www.facebook.com")
# elif "open twitter" in text2:
#     speak("Opening Twitter")
#     webbrowser.open("https://www.twitter.com")
# elif "open instagram" in text2:
#     speak("Opening Instagram")
#     webbrowser.open("https://www.instagram.com")
# elif "open linkedin" in text2:
#     speak("Opening LinkedIn")
#     webbrowser.open("https://www.linkedin.com")

# elif "news" in text2:
#     print("sure mam ! let me read news for you")
#     speak("sure mam ! let me read news for you")


#     arr=news()
#     for i in range(len(arr)):
#         speak(arr[i])
#         print(arr[i])
# elif "fact" in text2 or "facts" in text2:
#     speak(" sure mam!")
#     x=randfacts.get_fact()
#     print(x)
#     speak("  Did you know that,"+x)
# else:
#     speak("Sorry, I can't open that.")
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import pywhatkit
import news
import weather
import selenium_web

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
        print(f"User said: {query}")
    except Exception:
        print("Say that again please...")
        return "None"
    return query.lower()

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("hello I am Jarvis your virtual voice assistant. How can I help you?")

if __name__ == "__main__":
    wishMe()
    while True:
        query = takeCommand()

        if query == "none":
            continue

        if "wikipedia" in query:
            speak("Searching Wikipedia...")
            try:
                results = wikipedia.summary(query.replace("wikipedia", ""), sentences=2)
                speak("According to Wikipedia")
                print(results)
                speak(results)
            except Exception:
                speak("Sorry, I could not find that on Wikipedia.")

        elif "open youtube" in query:
            webbrowser.open("https://youtube.com")

        elif "open google" in query:
            webbrowser.open("https://google.com")

        elif "play" in query:
            song = query.replace("play", "")
            speak(f"Playing {song}")
            pywhatkit.playonyt(song)

        elif "news" in query:
            news.get_news()

        elif "weather" in query:
            speak("Tell me the city name")
            city = takeCommand()
            weather.get_weather(city)

        elif "search" in query:
            speak("What should I search?")
            search_term = takeCommand()
            selenium_web.open_google_and_search(search_term)

        elif "exit" in query or "quit" in query:
            speak("Goodbye!")
            break

        else:
            speak("Sorry, I didn't understand that.")
