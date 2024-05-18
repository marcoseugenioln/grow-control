import time
import board
import adafruit_dht
import threading
import queue
from .database import Database

class DHT():

    def __init__(self, database: Database):
        
        # sensor instance
        self.sensor = adafruit_dht.DHT11(board.D18)
        self.database = database
        dht_sensor_thread=threading.Thread(target=self.update, daemon=True)
        dht_sensor_thread.start()
        time.sleep(2)


    def update(self):

        while True:
            time.sleep(1)
            try:
                self.database.set_temperature(self.sensor.temperature)
                self.database.set_humidity(self.sensor.humidity)

            except RuntimeError as error:
                print(error.args[0])
                time.sleep(2.0)
                continue
    

    def get_temperature(self):
        temperature = self.database.get_temperature()[0][0]
        return temperature
    
    def get_humidity(self):
        humidity = self.database.get_humidity()[0][0]
        return humidity
    
# dht = DHT()

# while True:
#     time.sleep(1)
#     print(dht.get_values())