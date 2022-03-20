import json
from flask import Flask, request, send_from_directory, Response
from tinydb import TinyDB, Query
import time
import speech_recognition as sr
from rpi_ws281x import PixelStrip, Color
import sounddevice as sd
import soundfile as sf
import threading
import random

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


# def rainbow_lights(strip, wait_ms=50):                    #method for 1st animation 
#     red = Color(255, 0 ,0)                           #colors are determined based on (r,g,b)
#     orange= Color(255, 165 ,0)
#     yellow= (255, 255, 0)
#     green = Color(127, 255, 0)
#     blue = Color(0, 191, 255)
#     purple = Color(153, 50, 204)
#     colors = [red, orange, yellow, green, blue, purple]     #colors are added to a list
#     num_pixels_per_color = int(strip.numPixels() / len(colors))
#     
#     for i, color in enumerate(colors):
#         for j in range(num_pixels_per_color):
#             strip.setPixelColor((i*num_pixels_per_color)+j, color)
#             strip.show()
#             time.sleep(wait_ms / 1000.0)


# wheel and rainbow cycle r from https://github.com/rpi-ws281x/rpi-ws281x-python/blob/master/examples/strandtest.py#L56
def wheel(pos):
#     color = list(np.random.choice(range(256), size=3))
#     return Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 10))
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

def play_music(file):
    data, fs = sf.read(file)
    sd.play(data, fs)
    pixels_thread = threading.Thread(target=colorWipe, args=(strip, Color(0, 255, 0), 10))
    pixels_thread.start()
    sd.wait()

def play_songs(songs):
    for song in songs:
        play_music(songs)

def do_command(command):
    print(f'received command {command}')
    smol_command = command.lower()
    if "play chill" in smol_command or "calm" in smol_command or "music" in smol_command :
        music_thread = threading.Thread(target=play_songs, args=(['LDR_Chemtrails.wav', 'IV.wav', 'FrenchSong.wav'],))
        music_thread.start()
        pixels_thread = threading.Thread(target=colorWipe, args=(strip, Color(0, 0, 255), 10))
        pixels_thread.start()
    elif "hyper" in smol_command or "play intense" in smol_command:
        music_thread = threading.Thread(target=play_music, args=('StarWars3.wav',))
        music_thread.start()
    elif "lights" in smol_command or "light" in smol_command or "lit" in smol_command or "rainbow" in smol_command:
        pixels_thread = threading.Thread(target=colorWipe, args=(strip, Color(255, 0, 0), 10))
        pixels_thread.start()
    elif "bye" in smol_command or "off" in smol_command:
        colorWipe(strip, Color(0, 0, 0), 10)
    else:
        print(f'unrecognized command: {command}')

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

app = Flask(__name__)

db = TinyDB('./db.json')

@app.route('/', methods=['GET'])
def hello_world():
    return app.send_static_file('index.html')

@app.route('/<path:path>', methods=['GET'])
def index_get(path):
    return send_from_directory('static', path)

@app.route('/books', methods=['GET'])
def books_get():
    all_rows = db.all()
    all_isbns = [row['isbn'] for row in all_rows]
    return Response(json.dumps(all_isbns), mimetype='application/json')

@app.route('/books', methods=['PUT'])
def books_put():
    isbn = request.args.get('isbn')
    query = Query()
    db.remove(query.isbn == isbn)
    db.insert({'isbn': isbn})
    return ('', 204)

@app.route('/books', methods=['DELETE'])
def books_delete():
    isbn = request.args.get('isbn')
    query = Query()
    db.remove(query.isbn == isbn)
    return ('', 204)

@app.route('/voice-command', methods=['GET'])
def on_voice_command():
    command = request.args.get('command')
    do_command(command)
    return ('', 204)

def speech_rec_fun():
    r.listen_in_background(m, callback)


# rainbow_lights(strip, 10)
speech_rec_thread = threading.Thread(target=speech_rec_fun)
speech_rec_thread.start()
speech_rec_thread.join()
rainbowCycle(strip)
app.run(host='0.0.0.0', ssl_context='adhoc')