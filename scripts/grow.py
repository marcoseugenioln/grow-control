import datetime

class Grow():

    def __init__(self,
                 auto_mode=False, 
                 min_humidity=0,
                 max_humidity=0,
                 lights_on_time="06:00",
                 lights_off_time="22:00") -> None:

        self.auto_mode = auto_mode
        self.temperature = 0
        self.humidity = 0
        self.lights_on_time = datetime.datetime.strptime(lights_on_time, '%H:%M').time()
        self.lights_off_time = datetime.datetime.strptime(lights_off_time, '%H:%M').time()
        self.min_humidity = min_humidity
        self.max_humidity = max_humidity

        self.humidifier_on = False
        self.lights_on = False

    def report_sensor_status(self, temperature, humidity):
        status_updated = False
        if int(temperature) != self.temperature:
            status_updated = True
            self.temperature = int(temperature)
        if int(humidity) != self.humidity:
            status_updated = True
            self.humidity = int(humidity) 
        if status_updated:
            print(f'{datetime.datetime.now()} - m_dht_report: temperature[{self.temperature}°C] humidity[{self.humidity}%]')

        self.automatic_mode_routine()

    def set_grow_settings(self, auto_mode, humidifier_on, min_humidity, max_humidity, lights_on, lights_on_time, lights_off_time):
        print(f'{datetime.datetime.now()} - m_grow_settings_cmd: auto_mode[{auto_mode}] humidifier_on[{humidifier_on}] min_humidity[{min_humidity}] max_humidity[{max_humidity}] humidifier_on[{lights_on}] lights_on_time[{lights_on_time}] lights_off_time[{lights_off_time}]')
        self.auto_mode = auto_mode
        
        self.min_humidity = int(min_humidity)
        self.max_humidity = int(max_humidity)
        
        self.lights_on_time = datetime.datetime.strptime(str(lights_on_time[0:5]), '%H:%M').time()
        self.lights_off_time = datetime.datetime.strptime(str(lights_off_time[0:5]), '%H:%M').time()

        if auto_mode:
            self.automatic_mode_routine()

        else:
            self.lights_on = lights_on
            self.humidifier_on = humidifier_on

        print(f'{datetime.datetime.now()} - m_grow_settings_cmd: auto_mode[{self.auto_mode}] humidifier_on[{self.humidifier_on}] min_humidity[{self.min_humidity}] max_humidity[{self.max_humidity}] humidifier_on[{self.lights_on}] lights_on_time[{self.lights_on_time}] lights_off_time[{self.lights_off_time}]')
        

    def automatic_mode_routine(self):
        if self.auto_mode:
            self.humidifier_on = self.humidity < self.min_humidity
            self.lights_on = datetime.datetime.now().time() <=  self.lights_off_time and datetime.datetime.now().time() >= self.lights_on_time
