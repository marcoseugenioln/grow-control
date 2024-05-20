import threading
import socket
from scripts.dht import DHT
from scripts.wind import Wind
from pubsub import pub

class Grow():

    def __init__(self, host = "127.0.0.1", port= 65433) -> None:

        self.host = host
        self.port = port
        
        self.temperature = 0
        self.humidity = 0
        self.ventilation_capacity =0
        self.circulation_capacity=0

        self.dht = DHT()
        self.wind = Wind()
        self.communication_controller = threading.Thread(target=self.communication_loop, daemon=True)

        pub.subscribe(self.m_dht, 'm_dht')
        pub.subscribe(self.m_wind, 'm_wind')

    def communication_loop(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            
            while True:
                s.listen()
                connection, address = s.accept()
                with connection:
                    data = f'{self.temperature} {self.humidity} {self.ventilation_capacity}'
                    print(data)
                    connection.sendall(data.encode())

    def request_grow_data(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.get_host(), self.get_port()))
            data = s.recv(1024).decode().split()
            return {'temperature': data[0], 'humidity': data[1], 'ventilation_capacity' : data[2]}
        
    def m_dht(self, temperature, humidity):
        self.temperature = temperature
        self.humidity = humidity

    def m_wind(self, ventilation_capacity, circulation_capacity):
        print('ventilation capacity set as: ' + str(ventilation_capacity))
        self.ventilation_capacity = ventilation_capacity
        self.circulation_capacity = circulation_capacity

    def start(self):
        self.dht.start()
        self.wind.start()
        self.communication_controller.start()

    def get_host(self):
        return self.host
    
    def get_port(self):
        return self.port
    
    def manual_wind_config_cmd(self, auto, ventilation, circulation, activation_time, deactivation_time):
        pub.sendMessage('m_manual_wind_config_cmd', 
                        auto=auto,
                        ventilation=ventilation, 
                        circulation=circulation, 
                        activation_time=activation_time,
                        deactivation_time=deactivation_time)


        

    

