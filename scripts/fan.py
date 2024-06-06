from scripts.database import Database
from pubsub import pub
import RPi.GPIO as GPIO
from gpiozero import PWMOutputDevice

class Fan():
    
    def __init__(self, pin = 18, frequency=25):
        self.pin = pin
        self.capacity = 0
        self.fan = PWMOutputDevice(pin=self.pin, frequency=frequency)

    def get_capacity(self):
        return self.capacity

    def set_capacity(self, capacity):
        if self.capacity != capacity:
            self.capacity = capacity
            self.fan.value = int(self.capacity)/100


    