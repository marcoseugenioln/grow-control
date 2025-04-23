# import RPi.GPIO as GPIO
import time
from pubsub import pub

class StateDevice():

    def __init__(self, pin=20):
        self.pin = pin
        self.on = False
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
    
    def power_on(self, on):
        if not self.power_on and on:
            self.power_on = True
            GPIO.output(self.pin, GPIO.HIGH)
        elif self.on and not on:
            self.on = False
            GPIO.output(self.pin, GPIO.HIGH)


