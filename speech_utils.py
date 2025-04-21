import speech_recognition as sr
import pyttsx3

def listen_to_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except:
        return "Sorry, I didn't catch that."

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 135)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

