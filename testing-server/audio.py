import speech_recognition as sr
import time

r = sr.Recognizer()

# Words that sphinx should listen closely for. 0-1 is the sensitivity
# of the wake word.
keywords = [("bookshelf", 1), ("hey bookshelf", 1), ]

source = sr.Microphone()
with source as m:
    r.adjust_for_ambient_noise(m)

def callback(recognizer, audio):  # this is called from the background thread

    try:
        speech_as_text = recognizer.recognize_google(audio, keyword_entries=keywords)
        print(speech_as_text)

        # Look for your "Ok Google" keyword in speech_as_text
        if "bookshelf" in speech_as_text or "hey bookshelf":
            recognize_main()

    except sr.UnknownValueError:
        print("Oops! Didn't catch that")


def recognize_main():
    print("Recognizing Main...")
    audio_data = r.listen(source, timeout=2)
    said = r.recognize_google(audio_data)
    print(f"Speech Recognition thinks you said {said}")


def start_recognizer():
    r.listen_in_background(source, callback)
    time.sleep(1000000)

start_recognizer()
