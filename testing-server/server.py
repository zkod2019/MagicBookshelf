import json
from flask import Flask, request, send_from_directory, Response
from tinydb import TinyDB, Query
import speech_recognition as sr
from rpi_ws281x import PixelStrip, Color
import sounddevice as sd
import soundfile as sf
import threading
import random
import RPi.GPIO as GPIO
import time
import threading

# LED strip configuration:
LED_COUNT = 300       
LED_PIN = 21          
LED_FREQ_HZ = 800000  
LED_DMA = 10          
LED_BRIGHTNESS = 255  
LED_INVERT = False    
LED_CHANNEL = 0       

# Define functions which animate LEDs
def colorWipe(strip, color, wait_ms=50):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

sd.default.device = 'bcm2835 Headphones'
print(sd.query_devices())

strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# wheel and rainbow cycle are from https://github.com/rpi-ws281x/rpi-ws281x-python/blob/master/examples/strandtest.py#L56
def wheel(pos):
# Generate rainbow colors across 0-255 positions
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

# creates rainbow animation that distributes itself across all pixels
def rainbowCycle(strip, wait_ms=20, iterations=1):
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

# based on the color passed, random LED lights turn on and off to create matrix/rain effect
def togglePixelRandomly(strip, i, color):
    time.sleep(random.uniform(0, 2))
    if color == 'green':
        strip.setPixelColor(i, Color(0, random.randrange(60, 255), 0))
    elif color == 'red':
        strip.setPixelColor(i, Color(random.randrange(60, 255), 0, 0))
    elif color == 'blue':
        strip.setPixelColor(i, Color(0, 0, random.randrange(60, 255)))

    strip.show()

    time.sleep(random.uniform(0, 2))
    strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

# flickers LED lights at random positions
def randomPosition(strip, color):
    indices = list(range(strip.numPixels()))
    random.shuffle(indices)
    for i in indices:
        pixelThread = threading.Thread(target=togglePixelRandomly, args=(strip, i, color))
        pixelThread.start()

# reads music file
def play_music(file):
    data, fs = sf.read(file)
    sd.play(data, fs)
    sd.wait()

# goes through a list of files and calls play_music on them
def play_songs(songs):
    for song in songs:
        play_music(song)

# starts threads of music and lights based on the voice command given
def do_command(command):
    print(f'received command {command}')
    smol_command = command.lower()
    if "piano" in smol_command or "play piano" in smol_command or "calm" in smol_command :
        music_thread = threading.Thread(target=play_songs, args=(['FrenchSong.wav', 'IV.wav'],))
        music_thread.start()
        pixels_thread = threading.Thread(target=colorWipe, args=(strip, Color(0, 0, 255), 10))
        pixels_thread.start()
    elif "music" in smol_command or "play song" in smol_command:
        music_thread = threading.Thread(target=play_music, args=('LDR_Chemtrails.wav',))
        music_thread.start()
        pixels_thread = threading.Thread(target=colorWipe, args=(strip, Color(0, 255, 0), 10))
        pixels_thread.start()
    elif "lights" in smol_command or "light" in smol_command or "lit" in smol_command or "rainbow" in smol_command:
        pixels_thread = threading.Thread(target=rainbowCycle, args=(strip,))
        pixels_thread.start()
    elif "matrix" in smol_command or "grass" in smol_command:
        pixels_thread = threading.Thread(target=randomPosition, args=(strip, "green"))
        pixels_thread.start()
    elif "rain" in smol_command or "tears" in smol_command:
        pixels_thread = threading.Thread(target=randomPosition, args=(strip, "blue"))
        pixels_thread.start()
    elif "love" in smol_command or "heart" in smol_command:
        pixels_thread = threading.Thread(target=randomPosition, args=(strip, "red"))
        pixels_thread.start()
    elif "bye" in smol_command or "off" in smol_command:
        colorWipe(strip, Color(0, 0, 0), 10)
    else:
        print(f'unrecognized command: {command}')

keywords = [("bookshelf", 1), ("hey bookshelf", 1), ("hey", 1), ("morning", 1),]

# recognizes keywords in background audio
def callback(recognizer, audio):
    try:
        speech_as_text = recognizer.recognize_sphinx(audio, keyword_entries=keywords)
        print(speech_as_text)
        if "bookshelf" in speech_as_text or "hey bookshelf" or "hey" or "morning":
            recognize_main()

    except sr.UnknownValueError:
        print("Oops! Didn't catch that")

# uses google cloud (no longer background audio)
def recognize_main():
    print("Listening for Command...")
    audio_data = r.listen(source, timeout=2)
    said = r.recognize_google(audio_data)
    print(f"Speech Recognition thinks you said {said}")
    do_command(said)

r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    r.adjust_for_ambient_noise(source)

app = Flask(__name__)

db = TinyDB('./db.json')

# server endpoints
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
    
# set up for the HC-SR04 sensor
def distance_measurement_thread_function():
    GPIO.setmode(GPIO.BCM)

    TRIG = 23
    ECHO = 24

    print ("Distance Measurement In Progress")

    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)

    GPIO.output(TRIG,False)
    print("Waiting for Sensor")
    time.sleep(2)
    print("Ready")

    distance_sensor_active = False
    animation_idx = 0

    animations = [
        (colorWipe, (strip, Color(255, 0, 0), 10)),
        (colorWipe, (strip, Color(229, 83, 0), 10)),
        (colorWipe, (strip, Color(255, 159, 0), 10)),
        (colorWipe, (strip, Color(0, 255, 0), 10)),
        (colorWipe, (strip, Color(0, 255, 255), 10)),
        (colorWipe, (strip, Color(143, 0, 255), 10)),
        (colorWipe, (strip, Color(248, 24, 148), 10)),
    ]

    while True:
        GPIO.output(TRIG,True)
        time.sleep(0.00001)
        GPIO.output(TRIG,False)

        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)

        if distance <= 10 and not distance_sensor_active:
            distance_sensor_active = True
            animation_idx = (animation_idx + 1) % len(animations)
            print (animation_idx)
            animation_deets = animations[animation_idx]
            thread = threading.Thread(target=animation_deets[0], args=animation_deets[1])
            thread.start()
            print("something is close !!!")
        
        if distance > 10 and distance_sensor_active:
            distance_sensor_active = False
            print("de activated !!!")
        
        time.sleep(0.2)

# these threads are always running in the background
distance_measurement_thread = threading.Thread(target=distance_measurement_thread_function)
distance_measurement_thread.start()
speech_rec_thread = threading.Thread(target=speech_rec_fun)
speech_rec_thread.start()
speech_rec_thread.join()
app.run(host='0.0.0.0', ssl_context='adhoc', port=8105)