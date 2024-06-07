import threading
import socket
import time
from scripts.dht import DHT
# from scripts.wind import Wind
from scripts.humidifier import Humidifier
from scripts.fan import Fan
from pubsub import pub
import RPi.GPIO

class Grow():

    def __init__(self, ventilation_pin = 19, circulation_pin = 18, dht_sensor_pin = 1, humidifier_pin = 20) -> None:

        RPi.GPIO.cleanup()

        self.auto_mode = False
        self.temperature = 0
        self.humidity = 0
        self.light_act_time = None
        self.light_deact_time = None
        self.desired_temperature = 0
        self.desired_humidity = 0

        self.dht = DHT(pin=dht_sensor_pin)
        # self.wind = Wind(ventilation_pin=ventilation_pin, circulation_pin=circulation_pin)
        self.ventilator = Fan(pin=ventilation_pin)
        self.circulator = Fan(pin=circulation_pin)
        self.humidifier = Humidifier(pin=humidifier_pin)

        pub.subscribe(self.m_dht_report, 'm_dht_report')
        pub.subscribe(self.m_grow_settings_cmd, 'm_grow_settings_cmd')
        pub.subscribe(self.m_wind_config_cmd, "m_wind_config_cmd")
        pub.subscribe(self.m_humidifier_cmd, 'm_humidifier_cmd')

        self.automatic_mode_controller = threading.Thread(target=self.automatic_mode_loop, daemon=True)

    def m_dht_report(self, temperature, humidity):
        self.temperature = int(temperature)
        self.humidity = int(humidity)

        print(f'temperature: {self.temperature}C, humidity: {self.humidity}%')

    def m_wind_config_cmd(self, ventilation_capacity, circulation_capacity):
        self.ventilator.set_capacity(ventilation_capacity)
        self.circulator.set_capacity(circulation_capacity)

    def m_grow_settings_cmd(self, auto_mode, desired_humidity, desired_temperature, light_act_time, light_deact_time):
        self.auto_mode = auto_mode
        self.desired_humidity = int(desired_humidity)
        self.desired_temperature = int(desired_temperature)
        self.light_act_time = light_act_time
        self.light_deact_time = light_deact_time

    def m_humidifier_cmd(self, on):
        if bool(on):
            self.humidifier.activate()
        else:
            self.humidifier.deactivate()
    
    def automatic_mode_loop(self):
        while True:
            time.sleep(1)
            if self.auto_mode:

                if self.desired_humidity != 0:
                    
                    if self.humidity < self.desired_humidity and self.humidifier.is_active() == False:
                        print('humidity bellow desired levels, activating humidifier')
                        self.humidifier.activate()

                    elif self.humidity >= self.desired_humidity and self.humidifier.is_active():
                        print('humidity above desired levels, deactivating humidifier')
                        self.humidifier.deactivate()
                    else:
                        continue
            else:
                continue
        
    def start(self):
        self.dht.start()
        self.automatic_mode_controller.start()
    
    def get_auto_mode(self):
        return self.auto_mode
    
    def set_auto_mode(self, auto_mode):
        self.auto_mode = auto_mode


        

    

