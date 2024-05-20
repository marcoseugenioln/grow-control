import time
from scripts.database import Database
from pubsub import pub
import RPi.GPIO as GPIO
from gpiozero import PWMLED
import datetime
import threading

class Wind():
    
    def __init__(self):

        self.automatic_mode = 0
        self.ventilation = 0
        self.circulation = 0
        self.activation_time = None
        self.deactivation_time = None

        self.wind_on = False

        self.automatic_ventilation_capacity = 100
        self.automatic_circulation_capacity = 100

        self.ventilation_fan = PWMLED(14)

        pub.subscribe(self.m_manual_wind_config_cmd, "m_manual_wind_config_cmd")
        pub.subscribe(self.m_automatic_wind_config_cmd, "m_automatic_wind_config_cmd")

        self.automatic_mode_thread= threading.Thread(target=self.autoamtic_mode_loop, daemon=True)

    def m_manual_wind_config_cmd(self, automatic_mode, ventilation, circulation, activation_time, deactivation_time):
        self.set_automatic_mode(automatic_mode)
        self.set_ventilation(ventilation)
        self.set_circulation(circulation)
        self.set_activation_time(activation_time)
        self.set_deactivation_time(deactivation_time)
        self.report()
    
    def m_automatic_wind_config_cmd(self, ventilation_capacity, circulation_capacity):
        self.automatic_ventilation_capacity = ventilation_capacity
        self.automatic_circulation_capacity = circulation_capacity
        self.report()

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
            print(f'updating automatic mode to {str(bool(automatic_mode))}')
            self.automatic_mode = automatic_mode

    def set_ventilation(self, ventilation):
        if self.ventilation != ventilation:
            print(f'updating ventilation capacity to {ventilation}%')
            self.ventilation = ventilation
            self.ventilation_fan.value = int(self.ventilation)/100

    def set_circulation(self, circulation):
        if self.circulation != circulation:
            print(f'updating circulation capacity to {circulation}%')
            self.circulation = circulation

    def set_activation_time(self, activation_time):
        if self.activation_time != activation_time:
            print(f'updating activation time to {activation_time}')
            self.activation_time = activation_time

    def set_deactivation_time(self, deactivation_time):
        if self.deactivation_time != deactivation_time:
            print(f'updating deactivation time to {deactivation_time}')
            self.deactivation_time = deactivation_time

    def autoamtic_mode_loop(self):

        while True:
            time.sleep(0.200)
            if bool(self.automatic_mode):

                is_on_time = (datetime.datetime.now().time() > time(self.activation_time)) and (datetime.datetime.now().time() < time(self.deactivation_time))
                ventilation_capacity_updated = self.ventilation_fan.value != self.automatic_ventilation_capacity

                if (is_on_time and not self.wind_on) or (ventilation_capacity_updated):
                    self.wind_on = True
                    self.ventilation_fan = self.automatic_ventilation_capacity

                elif not is_on_time and self.wind_on:
                    self.wind_on = False
                    self.ventilation_fan = 0

                else:
                    continue
    
    def report(self):
        if bool(self.automatic_mode):
            pub.sendMessage('m_wind', ventilation_capacity=self.automatic_ventilation_capacity, circulation_capacity=self.automatic_circulation_capacity)
        else:
            pub.sendMessage('m_wind', ventilation_capacity=self.ventilation, circulation_capacity=self.circulation)

    def start(self):
        self.automatic_mode_thread.start()


    