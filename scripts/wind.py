import time
from scripts.database import Database
from pubsub import pub
import RPi.GPIO as GPIO
from gpiozero import PWMLED

class Wind():
    
    def __init__(self, database: Database):
        self.database=database
        self.automatic_mode = self.database.get_auto()[0][0]
        self.ventilation = self.database.get_ventilation()[0][0]
        self.circulation = self.database.get_circulation()[0][0]
        self.activation_time = self.database.get_act_time()[0][0]
        self.deactivation_time = self.database.get_deact_time()[0][0]

        self.ventilation_fan = PWMLED(14)
        self.ventilation_fan.value = self.ventilation

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
            print(f'updating automatic mode to {str(bool(automatic_mode))}')
            self.automatic_mode = automatic_mode
            self.database.set_auto(self.automatic_mode)

    def set_ventilation(self, ventilation):

        if self.ventilation != ventilation:
            print(f'updating ventilation capacity to {ventilation}%')
            self.ventilation = ventilation
            self.ventilation_fan.value = int(self.ventilation)/100
            self.database.set_ventilation(self.ventilation)

    def set_circulation(self, circulation):
        if self.circulation != circulation:
            print(f'updating circulation capacity to {circulation}%')
            self.circulation = circulation
            self.database.set_circulation(self.circulation)

    def set_activation_time(self, activation_time):
        if self.activation_time != activation_time:
            print(f'updating activation time to {activation_time}')
            self.activation_time = activation_time
            self.database.set_act_time(self.activation_time)

    def set_deactivation_time(self, deactivation_time):
        if self.deactivation_time != deactivation_time:
            print(f'updating deactivation time to {deactivation_time}')
            self.deactivation_time = deactivation_time
            self.database.set_deact_time(self.deactivation_time)
    