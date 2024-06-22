import time
import datetime
import adafruit_dht
import threading
from pubsub import pub
import RPi.GPIO as GPIO
from adafruit_blinka.microcontroller.bcm283x.pin import Pin

class DHT():

    def __init__(self, interval=10, input_pin=16, power_pin=1, max_error_count = 10):
        self.input_pin = input_pin
        self.power_pin = power_pin
        self.interval = interval
        self.sensor = adafruit_dht.DHT22(Pin(self.input_pin), False)
        self.max_error_count = max_error_count
        self.on = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.power_pin, GPIO.OUT)

        self.temperature = 0
        self.humidity = 0

        self.error_count = 0

        self.dht_thread=threading.Thread(target=self.loop, daemon=True)


    def is_active(self):
        return self.on

    def activate(self, on):

        # turn power supply on if not active
        if not self.is_active() and on:
            self.on = True
            GPIO.output(self.power_pin, GPIO.HIGH)
            print(f'{datetime.datetime.now()} - dht power supply: on')

        # turn power supply down if active
        elif self.is_active() and not on:
            self.on = False
            GPIO.output(self.power_pin, GPIO.LOW)
            print(f'{datetime.datetime.now()} - dht power supply: off')

    def get_temperature(self):
        return self.temperature
    
    def get_humidity(self):
        return self.humidity

    def loop(self):
        self.activate(True)
        while True:
            time.sleep(self.interval)
            try:
                self.temperature = self.sensor.temperature
                self.humidity = self.sensor.humidity
                print(f'{datetime.datetime.now()} - dht report: [{self.temperature}, {self.humidity}]')
                pub.sendMessage('m_dht_report', temperature=self.temperature, humidity=self.humidity)

            except RuntimeError as error:
                print(f'{datetime.datetime.now()} - dht report: {error}' )
                if str(error) == 'DHT sensor not found, check wiring':
                    self.error_count += 1

                if self.error_count >= self.max_error_count:
                    print(f'{datetime.datetime.now()} - DHT Sensor not responding, resetting sensor.')
                    self.reset_sensor()
                    self.error_count = 0

                time.sleep(self.interval)
                continue

            except Exception as error:
                self.reset_sensor()
                continue
    
    def reset_sensor(self):

        # deactivate sensor power supply
        self.activate(False)

        # call class destructor
        self.sensor.exit()

        # wait interval time
        time.sleep(self.interval)

        # reactivate power supply
        self.activate(True)

        # create sensor instance again
        self.sensor = adafruit_dht.DHT22(Pin(self.input_pin), False)

    def start(self):
        self.dht_thread.start()
        time.sleep(self.interval)

# ------------ register listener ------------------

# def dht_listener(temperature, humidity):
#     print("temperature: " + str(temperature))
#     print("humidity:    " + str(humidity))

# pub.subscribe(dht_listener, 'm_dht_report')

# dht = DHT()

# dht.start()

# while True:
#     time.sleep(5)