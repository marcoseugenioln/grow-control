from pubsub import pub
import RPi.GPIO as GPIO
from gpiozero import PWMOutputDevice

class PWMDevice():
    
    def __init__(self, pin = 18, frequency=25):
        self.pin = pin
        self.capacity = 0
        self.frequency = frequency
        self.device = PWMOutputDevice(pin=self.pin, frequency=self.frequency)

    def set_frequency(self, frequency):
        if self.frequency != frequency:
            self.frequency = frequency
            self.device = PWMOutputDevice(pin=self.pin, frequency=self.frequency)

    def set_capacity(self, capacity):
        if self.capacity != capacity:
            self.capacity = capacity
            self.device.value = int(self.capacity)/100
