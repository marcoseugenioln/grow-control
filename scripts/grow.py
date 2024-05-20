import threading
import socket
from scripts.dht import DHT
from pubsub import pub

class Grow():

    def __init__(self, host = "127.0.0.1", port= 65433) -> None:

        self.host = host
        self.port = port
        
        self.temperature = 0
        self.humidity = 0

        self.dht_controller = DHT()
        self.communication_controller = threading.Thread(target=self.communication_loop, daemon=True)

        pub.subscribe(self.m_dht, 'm_dht')

    def communication_loop(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            
            while True:
                s.listen()
                connection, address = s.accept()
                with connection:
                    connection.sendall(f'{self.temperature} {self.humidity}'.encode())

    def request_grow_data(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.get_host(), self.get_port()))
            data = s.recv(1024).decode().split()
            return {'temperature': data[0], 'humidity': data[1]}
        
    def m_dht(self, temperature, humidity):
        self.temperature = temperature
        self.humidity = humidity

    def start(self):
        self.dht_controller.start()
        self.communication_controller.start()

    def get_host(self):
        return self.host
    
    def get_port(self):
        return self.port
    
    def wind_config_cmd(self, auto, ventilation, circulation, activation_time, deactivation_time):
        pub.sendMessage('m_wind_config_cmd', 
                        auto=auto,
                        ventilation=ventilation, 
                        circulation=circulation, 
                        activation_time=activation_time,
                        deactivation_time=deactivation_time)


        

    

