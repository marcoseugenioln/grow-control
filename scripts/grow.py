import threading
import socket
import time
from scripts.dht import DHT
from scripts.wind import Wind
from scripts.humidifier import Humidifier
from pubsub import pub
import RPi.GPIO

class Grow():

    def __init__(self, host = "127.0.0.1", port= 65433) -> None:

        RPi.GPIO.cleanup()

        self.host = host
        self.port = port

        self.auto_mode = False
        self.temperature = 0
        self.humidity = 0
        self.light_act_time = None
        self.light_deact_time = None
        self.desired_temperature = 0
        self.desired_humidity = 0

        self.dht = DHT()
        self.wind = Wind()
        self.humidifier = Humidifier()

        pub.subscribe(self.m_grow_settings_cmd, 'm_grow_settings_cmd')
        pub.subscribe(self.m_dht, 'm_dht')

        self.automatic_mode_controller = threading.Thread(target=self.automatic_mode_loop, daemon=True)

    def m_dht(self, temperature, humidity):
        self.temperature = int(temperature)
        self.humidity = int(humidity)

        print(f'temperature: {self.temperature}C, humidity: {self.humidity}%')

    def m_grow_settings_cmd(self, auto_mode, desired_humidity, desired_temperature, light_act_time, light_deact_time):
        self.auto_mode = auto_mode
        self.desired_humidity = int(desired_humidity)
        self.desired_temperature = int(desired_temperature)
        self.light_act_time = light_act_time
        self.light_deact_time = light_deact_time
    
    def automatic_mode_loop(self):
        while True:
            time.sleep(1)
            if self.auto_mode:

                if self.desired_humidity != 0:
                    
                    if self.humidity < self.desired_humidity and self.humidifier.is_active() == False:
                        pub.sendMessage('m_humidifier_cmd', on=True)
                        print('humidity bellow desired levels, activating humidifier')

                    elif self.humidity >= self.desired_humidity and self.humidifier.is_active():
                        pub.sendMessage('m_humidifier_cmd', on=False)
                        print('humidity above desired levels, deactivating humidifier')
                    else:
                        continue
            else:
                continue
        
    def start(self):
        self.dht.start()
        self.automatic_mode_controller.start()

    def get_host(self):
        return self.host
    
    def get_port(self):
        return self.port
    
    def get_auto_mode(self):
        return self.auto_mode
    
    def set_auto_mode(self, auto_mode):
        self.auto_mode = auto_mode


        

    

