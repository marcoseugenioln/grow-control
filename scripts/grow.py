import threading
import datetime
import time
import math
from scripts.dht import DHT
from scripts.humidifier import Humidifier
from scripts.heater import Heater
from scripts.fan import Fan
from pubsub import pub
import RPi.GPIO

class Grow():

    def __init__(self, 
                 ventilator_pin=19, 
                 circulator_pin = 18, 
                 dht_sensor_pin = 1, 
                 humidifier_pin = 20, 
                 heater_pin = 15,
                 automatic=False, 
                 ventilator_capacity=0, 
                 circulator_capacity=0,
                 desired_humidity=0,
                 desired_temperature=0,
                 humidity_tolerance=0) -> None:

        RPi.GPIO.cleanup()

        self.auto_mode = automatic
        self.temperature = 0
        self.humidity = 0
        self.light_act_time = None
        self.light_deact_time = None
        self.desired_temperature = desired_temperature
        self.desired_humidity = desired_humidity
        self.humidity_tolerance = humidity_tolerance
        self.humidity_above_desired = False
        self.humidity_bellow_desired = False
        self.humidity_difference = 0

        # components
        self.dht = DHT(input_pin=dht_sensor_pin)
        self.ventilator = Fan(pin=ventilator_pin)
        self.circulator = Fan(pin=circulator_pin)
        self.humidifier = Humidifier(pin=humidifier_pin)
        self.heater = Heater(pin=heater_pin)

        self.ventilator.set_capacity(ventilator_capacity)
        self.circulator.set_capacity(circulator_capacity)

        pub.subscribe(self.m_dht_report, 'm_dht_report')
        pub.subscribe(self.m_grow_settings_cmd, 'm_grow_settings_cmd')

        self.automatic_mode_controller = threading.Thread(target=self.automatic_mode_loop, daemon=True)

    def m_dht_report(self, temperature, humidity):

        report_updated = False

        if int(temperature) != self.temperature:
            report_updated = True
            self.temperature = int(temperature)

        if int(humidity) != self.humidity:
            report_updated = True
            self.humidity = int(humidity) 
        
        if report_updated:
            print(f'{datetime.datetime.now()} - temperature: {self.temperature}°C - humidity: {self.humidity}%')

    def m_grow_settings_cmd(self, auto_mode, desired_humidity, desired_temperature, light_act_time, light_deact_time, ventilation_capacity, circulation_capacity, humidifier_on, heater_on):
        self.auto_mode = auto_mode
        self.desired_humidity = int(desired_humidity)
        self.desired_temperature = int(desired_temperature)
        self.light_act_time = light_act_time
        self.light_deact_time = light_deact_time
        
        self.ventilator.set_capacity(ventilation_capacity)
        self.circulator.set_capacity(circulation_capacity)
        self.humidifier.activate(humidifier_on)
        self.heater.activate(heater_on)

        print(f'{datetime.datetime.now()} - m_grow_settings_cmd:')
        print(f'auto_mode[{self.auto_mode}]')
        print(f'desired_humidity[{self.desired_humidity}]')
        print(f'desired_temperature[{self.desired_temperature}]')
        print(f'light_act_time[{self.light_act_time}]')
        print(f'light_deact_time[{self.light_deact_time}]')
        print(f'ventilator_capacity[{ventilation_capacity}]')
        print(f'circulator_capacity[{circulation_capacity}]')
        print(f'humidifier_on[{humidifier_on}]')

    def humidifier_automatic_regulation(self):
        if self.desired_humidity != 0:
            if self.humidity_bellow_desired and not self.humidifier.is_active():
                print(f'{datetime.datetime.now()} - humidifier: on')
                self.humidifier.activate(True)

            elif self.humidity >= self.desired_humidity and self.humidifier.is_active():
                print(f'{datetime.datetime.now()} - humidifier: off')
                self.humidifier.activate(False)

    def ventilator_automatic_regulation(self):

        capacity = 0

        if self.humidity_above_desired and self.humidity_diference > self.humidity_tolerance:
            capacity = 100

        elif self.humidity_above_desired and self.humidity_diference <= self.humidity_tolerance:
            capacity = 95

        elif not self.humidity_above_desired and not self.humidity_bellow_desired:
            capacity = 90

        elif self.humidity_bellow_desired and self.humidity_diference <= self.humidity_tolerance:
            capacity = 85

        elif self.humidity_bellow_desired and self.humidity_diference > self.humidity_tolerance:
            capacity = 80

        if self.ventilator.get_capacity() != capacity:
            print(f'{datetime.datetime.now()} - setting ventilator capacity to: {capacity}%')
            self.ventilator.set_capacity(capacity)


    def automatic_mode_loop(self):
        while True:

            time.sleep(1)
            if self.auto_mode:

                self.humidity_above_desired = self.humidity > self.desired_humidity
                self.humidity_bellow_desired = self.humidity < self.desired_humidity 
                self.humidity_diference = math.sqrt(math.pow(self.humidity - self.desired_humidity, 2))
                
                self.humidifier_automatic_regulation()
                self.ventilator_automatic_regulation()
            else:
                continue
        
    def start(self):
        self.dht.start()
        self.automatic_mode_controller.start()
    
    def get_auto_mode(self):
        return self.auto_mode
    
    def set_auto_mode(self, auto_mode):
        self.auto_mode = auto_mode


        

    

