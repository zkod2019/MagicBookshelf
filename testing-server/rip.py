int ledPin = 13;  // LED on Pin 13 of Arduino
int pirPin = 7; // Input for HC-S501(PIR-sensor)
int pirValue; // Place to store read PIR Value

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(pirPin, INPUT);
  digitalWrite(ledPin, LOW);
  Serial.begin(9600);
}

void loop() {
    pirValue = digitalRead(pirPin);
    digitalWrite(ledPin, pirValue);
    if(pirValue==HIGH){
      Serial.println("1");
      pirValue=0;
    }
}

# import RPi.GPIO as GPIO
# import time
#  
# SENSOR_PIN = 20
# # https://tutorials-raspberrypi.com/connect-and-control-raspberry-pi-motion-detector-pir/
# 
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(SENSOR_PIN, GPIO.IN)
#  
# def my_callback(channel):
#     # Here, alternatively, an application / command etc. can be started.
#     print('There was a movement!')
# 
# try:
#     GPIO.add_event_detect(SENSOR_PIN , GPIO.RISING, callback=my_callback)
#     while True:
#         time.sleep(10)
# except KeyboardInterrupt:
#     print ("Finish...")
# GPIO.cleanup()