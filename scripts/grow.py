import threading
import datetime
import time
from scripts.dht import DHT
from scripts.humidifier import Humidifier
from scripts.fan import Fan
from pubsub import pub
import RPi.GPIO

class Grow():

    def __init__(self, 
                 ventilator_pin=19, 
                 circulator_pin = 18, 
                 dht_sensor_pin = 1, 
                 humidifier_pin = 20, 
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
        self.humidity_tolerance=humidity_tolerance

        # components
        self.dht = DHT(pin=dht_sensor_pin)
        self.ventilator = Fan(pin=ventilator_pin)
        self.circulator = Fan(pin=circulator_pin)
        self.humidifier = Humidifier(pin=humidifier_pin)

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
            print(f'temperature: {self.temperature}°C - humidity: {self.humidity}% - time: {datetime.datetime.now()}')

    def m_grow_settings_cmd(self, auto_mode, desired_humidity, desired_temperature, light_act_time, light_deact_time, ventilation_capacity, circulation_capacity, humidifier_on):
        self.auto_mode = auto_mode
        self.desired_humidity = int(desired_humidity)
        self.desired_temperature = int(desired_temperature)
        self.light_act_time = light_act_time
        self.light_deact_time = light_deact_time
        self.ventilator.set_capacity(ventilation_capacity)
        self.circulator.set_capacity(circulation_capacity)
        self.humidifier.activate(humidifier_on)
    
    def automatic_mode_loop(self):
        while True:
            time.sleep(1)
            if self.auto_mode:
                if self.desired_humidity != 0:
                    if self.humidity < self.desired_humidity and self.humidifier.is_active() == False:
                        print('humidity bellow desired levels, activating humidifier')
                        self.humidifier.activate(True)

                        if self.ventilator.get_capacity() < 40:
                            self.ventilator.set_capacity(40)

                    elif self.humidity >= self.desired_humidity and self.humidifier.is_active():
                        print('humidity above desired levels, deactivating humidifier')
                        self.humidifier.activate(False)
                    else:
                        continue

                    humidity_diference = self.humidity - self.desired_humidity

                    # humidity levels above desired and tolerance
                    if humidity_diference > 0 and humidity_diference > self.humidity_tolerance:
                        self.ventilator.set_capacity(100)
                    elif humidity_diference > 0 and humidity_diference <= self.humidity_tolerance:
                        self.ventilator.set_capacity(90)
                    elif humidity_diference == 0:
                        self.ventilator.set_capacity(80)
                    elif humidity_diference < 0 and (humidity_diference*-1) <= self.humidity_tolerance:
                        self.ventilator.set_capacity(70)
                    elif humidity_diference < 0 and (humidity_diference*-1) > self.humidity_tolerance:
                        self.ventilator.set_capacity(50)

            else:
                continue
        
    def start(self):
        self.dht.start()
        self.automatic_mode_controller.start()
    
    def get_auto_mode(self):
        return self.auto_mode
    
    def set_auto_mode(self, auto_mode):
        self.auto_mode = auto_mode


        

    

