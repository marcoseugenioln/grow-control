import RPi.GPIO as GPIO
import time
from pubsub import pub

class Humidifier():

    def __init__(self, pin=20):
        self.pin = pin
        self.on = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def is_active(self):
        return self.on
    
    def activate(self, on):
        if not self.is_active() and on:
            self.on = True
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.pin, GPIO.LOW)

        elif self.is_active() and not on:
            self.on = False
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.pin, GPIO.LOW)    


