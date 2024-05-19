import threading
import time
from scripts.database import Database

class Wind():
    
    def __init__(self, database: Database):
        self.database=database
        self.auto = self.database.get_auto()[0][0]
        self.ventilation = self.database.get_ventilation()[0][0]
        self.circulation = self.database.get_circulation()[0][0]
        self.act_time = self.database.get_act_time()[0][0]
        self.deact_time = self.database.get_deact_time()[0][0]
        

        self.wind_thread=threading.Thread(target=self.loop, daemon=True)
        self.wind_thread.start()

    def loop(self):
        
        previous_auto        = self.auto
        previous_ventilation = self.ventilation
        previous_circulation = self.circulation
        previous_act_time    = self.act_time
        previous_deact_time  = self.deact_time

        while True:
            time.sleep(0.200)
            if self.auto != previous_auto:
                print('auto mode updated: ' + str(self.auto))
                previous_auto = self.auto

            if self.ventilation != previous_ventilation:
                print('ventilation updated: ' + str(self.ventilation))
                previous_ventilation = self.ventilation

            if self.circulation != previous_circulation:
                print('circulation updated: ' + str(self.circulation))
                previous_circulation = self.circulation

            if self.act_time != previous_act_time:
                print('activation time updated: ' + str(self.act_time))
                previous_act_time = self.act_time

            if self.deact_time != previous_deact_time:
                print('deactivation time updated: ' + str(self.deact_time))
                previous_deact_time = self.deact_time

    def get_auto(self):
        return self.auto
    
    def get_ventilation(self):
        return self.ventilation
    
    def get_circulation(self):
        return self.circulation
    
    def get_act_time(self):
        return self.act_time
    
    def get_deact_time(self):
        return self.deact_time
    
    def set_auto(self, auto):
        self.auto = auto
        self.database.set_auto(self.auto)

    def set_ventilation(self, ventilation):
        self.ventilation = ventilation
        self.database.set_ventilation(self.ventilation)

    def set_circulation(self, circulation):
        self.circulation = circulation
        self.database.set_circulation(self.circulation)

    def set_act_time(self, act_time):
        self.act_time = act_time
        self.database.set_act_time(self.act_time)

    def set_deact_time(self, deact_time):
        self.deact_time = deact_time
        self.database.set_deact_time(self.deact_time)
    