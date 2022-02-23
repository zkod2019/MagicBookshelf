import sounddevice as sd
import soundfile as sf

sd.default.device = 'bcm2835 Headphones'
print(sd.query_devices())

data, fs = sf.read('StarWars3.wav')
sd.play(data, fs)
sd.wait()
