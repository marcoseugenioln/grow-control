# from scripts.database import Database
from pubsub import pub
import RPi.GPIO as GPIO
from gpiozero import PWMLED
from gpiozero import PWMOutputDevice

class Wind():
    
    def __init__(self, ventilation_pin = 19, circulation_pin = 18):

        self.ventilation_pin = ventilation_pin
        self.circulation_pin = circulation_pin

        self.ventilation_capacity = 0
        self.circulation_capacity = 0

        self.wind_on = False

        self.ventilation_fan = PWMOutputDevice(pin=self.ventilation_pin, frequency=25)
        self.circulation_fan = PWMOutputDevice(pin=self.circulation_pin, frequency=25)

        pub.subscribe(self.m_wind_config_cmd, "m_wind_config_cmd")

    def m_wind_config_cmd(self, ventilation_capacity, circulation_capacity):
        self.set_ventilation_capacity(ventilation_capacity)
        self.set_circulation_capacity(circulation_capacity)

    def get_ventilation_capacity(self):
        return self.ventilation_capacity
    
    def get_circulation_capacity(self):
        return self.circulation_capacity

    def set_ventilation_capacity(self, ventilation_capacity):
        if self.ventilation_capacity != ventilation_capacity:
            self.ventilation_capacity = ventilation_capacity
            self.ventilation_fan.value = int(self.ventilation_capacity)/100

    def set_circulation_capacity(self, circulation_capacity):
        if self.circulation_capacity != circulation_capacity:
            self.circulation_capacity = circulation_capacity
            self.circulation_fan.value = int(self.circulation_capacity)/100


    