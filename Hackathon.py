import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import datetime
import webbrowser
import wikipedia
import os
import psutil
from groq import Groq
import edge_tts
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv(GROQ_API_KEY)
client = Groq(api_key=GROQ_API_KEY)
def remember_context(text):
    with open("context_memory.txt", "a") as file:
        file.write(text + "\n")

def load_context():
    if not os.path.exists("context_memory.txt"):
        return ""
    with open("context_memory.txt", "r") as file:
        return file.read().strip()

async def speak_async(text, voice="en-US-JennyNeural"):
    print(f"\nMentor: {text}\n")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("voice.mp3")
    playsound("voice.mp3")
    os.remove("voice.mp3")

def speak(text):
    asyncio.run(speak_async(text))

def listen():
    recognizer = sr.Recognizer()
    full_command = ""

    with sr.Microphone() as source:
        print("🎤 Listening... ")
        recognizer.adjust_for_ambient_noise(source)

        while True:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                command = recognizer.recognize_google(audio)
                print(f"You: {command}")
                full_command += " " + command.lower()

                if any(stop_phrase in command.lower() for stop_phrase in ["that's it", "okay done", "that's all"]):
                    break

            except sr.WaitTimeoutError:
                print("⏳ Listening timed out. Waiting for next input...")
                break
            except sr.UnknownValueError:
                speak("Sorry, I didn't catch that.")
                break
            except sr.RequestError:
                speak("Network error. Please check your connection.")
                break

    return full_command.strip()

def ask_groq(prompt):
    try:
        chat = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful, human-like mentor. Respond friendly, very short, and useful."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.6,
            max_tokens=200,
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I couldn't generate a response. ({e})"

def greet():
    hour = int(datetime.datetime.now().hour)
    if 5 <= hour < 12:
        speak("Good morning!")
    elif 12 <= hour < 18:
        speak("Good afternoon!, Hi how can i help you, Don't disturb me again,  Just Joking")
    else:
        speak("Hi , How are you, How can i help you")

def main():
    greet()
    while True:
        command = listen()
        if not command:
            continue

        if "time" in command:
            now = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {now}")
            continue

        elif "wikipedia" in command:
            speak("Searching Wikipedia...")
            try:
                topic = command.replace("wikipedia", "").strip()
                summary = wikipedia.summary(topic, sentences=2)
                speak(summary)
            except:
                speak("Sorry, couldn't find that.")
            continue

        elif "open youtube" in command:
            webbrowser.open("https://youtube.com")
            speak("Opening YouTube")
            continue

        elif "open google" in command:
            webbrowser.open("https://google.com")
            speak("Opening Google")
            continue

        elif "battery" in command:
            battery = psutil.sensors_battery()
            percent = battery.percent
            speak(f"Battery is at {percent} percent")
            continue

        elif "exit" in command or "bye" in command or "stop" in command:
            speak("Goodbye! and don't disturb me again ")
            break

        if any(word in command for word in ["idea", "project", "app", "build", "develop", "hackathon"]):
            remember_context(command)

        context = load_context()
        prompt = (
            "Keep your respose short and sweet, keep 2 to 3 snetences "
            "You are an AI mentor helping a student prepare for a hackathon.\n"
            "Your job is to give useful, practical suggestions like a smart and helpful teammate.\n"
            "Speak casually and sometimes add a bit of humor or teasing to make it feel friendly and human.\n"
            "Always use your full technical knowledge, but keep replies short and clear.\n\n"
            f"Session memory:\n{context}\n\n"
            f"Current input: {command}"
        )

        response = ask_groq(prompt)
        speak(response)

if __name__ == "__main__":
    main()
