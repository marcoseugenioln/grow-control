import threading
import datetime
import time
from scripts.dht import DHT
from scripts.pwm_device import PWMDevice
from scripts.state_device import StateDevice
from pubsub import pub
# import RPi.GPIO

class Grow():

    def __init__(self,
                 humidifier_pin = 20, 
                 lights_pin = 99,
                 auto_mode=False, 
                 min_humidity=0,
                 max_humidity=0,
                 lights_on_time="06:00",
                 lights_off_time="22:00") -> None:

        RPi.GPIO.cleanup()

        self.auto_mode = auto_mode
        self.temperature = 0
        self.humidity = 0
        self.lights_on_time = datetime.datetime.strptime(lights_on_time, '%H:%M').time()
        self.lights_off_time = datetime.datetime.strptime(lights_off_time, '%H:%M').time()
        self.min_humidity = min_humidity
        self.max_humidity = max_humidity

        # components
        self.lights = StateDevice(pin=lights_pin)
        self.humidifier = StateDevice(pin=humidifier_pin)

        pub.subscribe(self.m_dht_report, 'm_dht_report')
        pub.subscribe(self.m_grow_settings_cmd, 'm_grow_settings_cmd')

    def m_dht_report(self, temperature, humidity):
        report_updated = False
        if int(temperature) != self.temperature:
            report_updated = True
            self.temperature = int(temperature)
        if int(humidity) != self.humidity:
            report_updated = True
            self.humidity = int(humidity) 
        if report_updated:
            print(f'{datetime.datetime.now()} - m_dht_report: temperature[{self.temperature}°C] humidity[{self.humidity}%]')

        self.automatic_mode_routine()

    def m_grow_settings_cmd(self, auto_mode, humidifier_on, min_humidity, max_humidity, lights_on, lights_on_time, lights_off_time):
        print(f'{datetime.datetime.now()} - m_grow_settings_cmd: auto_mode[{auto_mode}] humidifier_on[{humidifier_on}] min_humidity[{min_humidity}] max_humidity[{max_humidity}] humidifier_on[{lights_on}] lights_on_time[{lights_on_time}] lights_off_time[{lights_off_time}]')
        self.auto_mode = auto_mode
        self.humidifier.power_on(humidifier_on)
        self.min_humidity = int(min_humidity)
        self.max_humidity = int(max_humidity)
        self.lights.power_on(lights_on)
        self.lights_on_time = datetime.datetime.strptime(str(lights_on_time[0:5]), '%H:%M').time()
        self.lights_off_time = datetime.datetime.strptime(str(lights_off_time[0:5]), '%H:%M').time()
        print(f'{datetime.datetime.now()} - m_grow_settings_cmd: auto_mode[{self.auto_mode}] humidifier_on[{self.humidifier.on}] min_humidity[{self.min_humidity}] max_humidity[{self.max_humidity}] humidifier_on[{self.lights.on}] lights_on_time[{self.lights_on_time}] lights_off_time[{self.lights_off_time}]')

        self.automatic_mode_routine()

    def humidifier_automatic_regulation(self):
        humidifier_on = False
        if self.humidity > self.max_humidity:
            humidifier_on = False
        elif self.humidity < self.min_humidity:
            humidifier_on = True
        self.humidifier.power_on(humidifier_on)

    def lights_automatic_regulation(self):
        lights_on = datetime.datetime.now().time() <=  self.lights_off_time and datetime.datetime.now().time() >= self.lights_on_time
        self.lights.power_on(lights_on)

    def automatic_mode_routine(self):
        if self.auto_mode:
            self.humidifier_automatic_regulation()
            self.lights_automatic_regulation()