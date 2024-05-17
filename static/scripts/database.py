import sqlite3

class Database():

    def __init__(self, path="schema.db",  schema="schema.sql", read_sql_file=True):

        self.connection = sqlite3.connect(path, check_same_thread=False, timeout=10)
        self.query = self.connection.cursor()

        if read_sql_file:

            with open(schema, 'r') as sql_file:
                sql_script = sql_file.read()

            self.query.executescript(sql_script)
            self.connection.commit()

    def run_query(self, query):
        print(query)
        self.query.execute(query)
        self.connection.commit()

        data = self.query.fetchall()
        print(data)
        if data:
            return data
        
    def get_auto(self):
        return self.run_query(f"select auto from wind where id == 1;")
    def get_ventilation(self):
        return self.run_query(f"select ventilation from wind where id == 1;")
    def get_circulation(self):
        return self.run_query(f"select circulation from wind where id == 1;")
    def get_act_time(self):
        return self.run_query(f"select act_time from wind where id == 1;")
    def get_deact_time(self):
        return self.run_query(f"select deact_time from wind where id == 1;")
    
    def set_auto(self, auto):
        self.run_query(f"update wind set auto = {auto} where id == 1;")
    def set_ventilation(self, ventilation):
        self.run_query(f"update wind set ventilation = {ventilation} where id == 1;")
    def set_circulation(self, circulation):
        self.run_query(f"update wind set circulation = {circulation} where id == 1;")
    def set_act_time(self, act_time):
        self.run_query(f"update wind set act_time = time('{act_time}') where id == 1;")
    def set_deact_time(self, deact_time):
        self.run_query(f"update wind set deact_time = time('{deact_time}') where id == 1;")