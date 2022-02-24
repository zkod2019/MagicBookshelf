import json
from flask import Flask, request, send_from_directory, Response
from tinydb import TinyDB, Query
import time
import speech_recognition as sr
from rpi_ws281x import PixelStrip, Color
import sounddevice as sd
import soundfile as sf
import threading

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

def play_music(file):
    data, fs = sf.read(file)
    sd.play(data, fs)
    pixels_thread = threading.Thread(target=colorWipe, args=(strip, Color(0, 255, 0), 10))
    pixels_thread.start()
    sd.wait()

def play_songs(songs):
    for song in song:
        play_music(songs)

def do_command(command):
    print(f'received command {command}')
    if command == "play chill" or command == "calm":
        music_thread = threading.Thread(target=play_songs, args=(['LDR_Chemtrails.wav', 'IV.wav', 'FrenchSong.wav'],))
        music_thread.start()
    elif command == "hyper" or command == "play intense":
        music_thread = threading.Thread(target=play_music, args=('StarWars3.wav',))
        music_thread.start()
    elif command == "lights" or command == "light" or command == "lit" or command == "rainbow":
        pixels_thread = threading.Thread(target=colorWipe, args=(strip, Color(255, 0, 0), 10))
        pixels_thread.start()
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

speech_rec_thread = threading.Thread(target=speech_rec_fun)
speech_rec_thread.start()
speech_rec_thread.join()
app.run(host='0.0.0.0', ssl_context='adhoc')
