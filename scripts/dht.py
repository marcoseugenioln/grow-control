import time
import board
import adafruit_dht
import threading
from pubsub import pub

class DHT():

    def __init__(self, interval=1):
        self.interval = interval
        self.sensor = adafruit_dht.DHT11(board.D18)

        self.temperature = 0
        self.humidity = 0

        self.dht_thread=threading.Thread(target=self.loop, daemon=True)

    def start(self):
        self.dht_thread.start()
        time.sleep(self.interval)

    def get_temperature(self):
        return self.temperature
    
    def get_humidity(self):
        return self.humidity

    def loop(self):
        while True:
            time.sleep(self.interval)
            try:
                self.temperature = self.sensor.temperature
                self.humidity = self.sensor.humidity

                pub.sendMessage('m_dht', temperature=self.temperature, humidity=self.humidity)

            except RuntimeError as error:
                print(error.args[0])
                time.sleep(self.interval)
                continue

# ------------ register listener ------------------

# def dht_listener(self, temperature, humidity):
#     print("temperature: " + str(temperature))
#     print("humidity:    " + str(humidity))

# pub.subscribe(dht_listener, 'm_dht')

# dht = DHT()

# dht.start()

# while True:
#     time.sleep(5)