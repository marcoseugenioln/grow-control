import RPi.GPIO as GPIO
import time
from pubsub import pub

class Humidifier():

    def __init__(self, pin=20):
        self.pin = pin
        self.on = False
        self.automatic_mode = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

        pub.subscribe(self.m_humidifier_cmd, 'm_humidifier_cmd')

    def is_active(self):
        return self.on
    
    def get_automatic_mode(self):
        return self.automatic_mode

    def m_humidifier_cmd(self, automatic_mode, on):
        print(automatic_mode, on)
        self.automatic_mode = automatic_mode

        if not self.automatic_mode:
            if bool(on):
                self.on = bool(on)
                GPIO.output(self.pin, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(self.pin, GPIO.LOW)
            else:
                self.on = False
                GPIO.output(self.pin, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(0.5)
                GPIO.output(self.pin, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(self.pin, GPIO.LOW)





