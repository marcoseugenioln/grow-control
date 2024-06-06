import RPi.GPIO as GPIO
import time
from pubsub import pub

class Humidifier():

    def __init__(self, pin=20):
        self.pin = pin
        self.on = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

        pub.subscribe(self.m_humidifier_cmd, 'm_humidifier_cmd')

    def is_active(self):
        return self.on
    
    def activate(self):
        if not self.is_active():
            self.on = True
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.pin, GPIO.LOW)

    def deactivate(self):
        if self.is_active():
            self.on = False
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.pin, GPIO.LOW)

    


