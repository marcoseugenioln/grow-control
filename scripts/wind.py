import time
from scripts.database import Database
from pubsub import pub
import RPi.GPIO as GPIO
from gpiozero import PWMLED
from gpiozero import PWMOutputDevice
import datetime
import threading

class Wind():
    
    def __init__(self, ventilation_pin = 14, circulation_pin = 18):

        self.ventilation_pin = ventilation_pin
        self.circulation_pin = circulation_pin

        self.automatic_mode = 0
        self.ventilation = 0
        self.circulation = 0
        self.activation_time = None
        self.deactivation_time = None

        self.wind_on = False

        self.ventilation_fan = PWMOutputDevice(pin=self.ventilation_pin, frequency=250)
        self.circulation_fan = PWMOutputDevice(pin=self.circulation_pin, frequency=250)

        pub.subscribe(self.m_wind_config_cmd, "m_wind_config_cmd")

    def m_wind_config_cmd(self, automatic_mode, ventilation, circulation, activation_time, deactivation_time):
        self.set_automatic_mode(automatic_mode)
        self.set_ventilation(ventilation)
        self.set_circulation(circulation)
        self.set_activation_time(activation_time)
        self.set_deactivation_time(deactivation_time)

    def get_automatic_mode(self):
        return self.automatic_mode
    
    def get_ventilation(self):
        return self.ventilation
    
    def get_circulation(self):
        return self.circulation
    
    def get_activation_time(self):
        return self.activation_time
    
    def get_deactivation_time(self):
        return self.deactivation_time
    
    def set_automatic_mode(self, automatic_mode):
        if self.automatic_mode != automatic_mode:
            self.automatic_mode = automatic_mode

    def set_ventilation(self, ventilation):
        if self.ventilation != ventilation:
            self.ventilation = ventilation
            self.ventilation_fan.value = int(self.ventilation)/100

    def set_circulation(self, circulation):
        if self.circulation != circulation:
            self.circulation = circulation
            self.circulation_fan.value = int(self.circulation)/100


    def set_activation_time(self, activation_time):
        if self.activation_time != activation_time and activation_time != None:
            self.activation_time = activation_time

    def set_deactivation_time(self, deactivation_time):
        if self.deactivation_time != deactivation_time and deactivation_time  != None:
            self.deactivation_time = deactivation_time


    