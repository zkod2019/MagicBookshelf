import time
import speech_recognition as sr
from rpi_ws281x import PixelStrip, Color
import sounddevice as sd
import soundfile as sf

# LED strip configuration:
LED_COUNT = 300       # Number of LED pixels.
LED_PIN = 21          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

sd.default.device = 'bcm2835 Headphones'
print(sd.query_devices())

strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def do_command(command):
    if command == "play chill":
        data, fs = sf.read('StarWars3.wav')
        sd.play(data, fs)
        sd.wait()
    elif command == "play intense":
        data, fs = sf.read('StarWars3.wav')
        sd.play(data, fs)
        sd.wait()
    elif command == "lights" or command == "light" or command == "lit":
        colorWipe(strip, Color(255, 0, 0), 10)
        colorWipe(strip, Color(0, 0, 0), 10)

def callback(recognizer, audio):
    try:
        said = recognizer.recognize_google(audio)
        print(f"Google Speech Recognition thinks you said {said}")
        do_command(said)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {format(e)}")


r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    r.adjust_for_ambient_noise(source)

r.listen_in_background(m, callback)

while True:
    time.sleep(0.1)
