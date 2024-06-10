import sqlite3
import datetime

class Database():

    def __init__(self, 
                 database_path="schema.db", 
                 schema_file="schema.sql",
                 read_sql_file=True):

        self.connection = sqlite3.connect(database_path, check_same_thread=False, timeout=10)
        self.query = self.connection.cursor()

        if read_sql_file:
            with open(schema_file, 'r') as sql_file:
                sql_script = sql_file.read()

            self.query.executescript(sql_script)
            self.connection.commit()

    def execute_query(self, query, fetch=False):
        print(f'{datetime.datetime.now()} - {query}')
        self.query.execute(query)
        self.connection.commit()

        retrieved_values = None

        if fetch:
            retrieved_values = self.query.fetchall()  

            if retrieved_values:
                return retrieved_values
            else:
                return []
        else:
            return retrieved_values
        
    def get_plants(self):
        return self.execute_query(f"select id, name, date, alive, harvested, photoperiod_id, gender_id from plant;", True)
    
    def insert_plant(self, name, date, photoperiod_id, gender_id):
        self.execute_query(f"insert into plant (name, date, photoperiod_id, gender_id) values ('{name}', DATE('{date}'), {photoperiod_id}, {gender_id});")

    def update_plant(self, id, name, date, alive, harvested, photoperiod_id, gender_id):
        self.execute_query(f"update plant set name = {name}, date = DATE('{date}'), alive = {alive}, harvested = {harvested}, photoperiod_id = {photoperiod_id}, gender_id = {gender_id} where id = {id};")
    
    def get_plant(self, id):
        return self.execute_query(f"select id, name, date, alive, harvested, photoperiod_id, gender_id from plant where id = {id};", True)

    def delete_plant(self, id):
        return self.execute_query(f"delete from plant where id = {id};", True)

    def get_trainings(self):
        return self.execute_query(f"select id, plant_id, training_type_id, date from training;", True)
    
    def get_plant_trainings(self, plant_id):
        return self.execute_query(f"select id, plant_id, training_type_id, date from training where plant_id = {plant_id};", True)
    
    def insert_training(self, plant_id, training_type_id, date):
        self.execute_query(f"insert into training (plant_id, training_type_id, date) values {plant_id}, {training_type_id}, DATE('{date}');")
    
    def get_waterings(self):
        return self.execute_query(f"select id, plant_id, date, mililiter from watering;", True)
    
    def get_plant_waterings(self, plant_id):
        return self.execute_query(f"select id, date, mililiter from watering where plant_id = {plant_id};", True)
    
    def insert_watering(self, plant_id, date, mililiter):
        self.execute_query(f"insert into watering (plant_id, date, mililiter) values {plant_id}, DATETIME('{date}'), {mililiter};")
    
    def get_feedings(self):
        return self.execute_query(f"select id, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium from feeding;", True)
    
    def get_plant_feedings(self, plant_id):
        return self.execute_query(f"select id, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium from feeding where plant_id = {plant_id};", True)
    
    def get_plant_waterings(self, plant_id):
        return self.execute_query(f"select id, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium from feeding where plant_id = {plant_id};", True)

    def insert_feeding(self, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium):
        self.execute_query(f"insert into watering (plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium) values {plant_id}, DATE('{date}'), {dosage}, {concentration}, {nitrogen}, {phosphorus}, {potassium};")
    
    def get_transplantings(self):
        return self.execute_query(f"select id, plant_id, date, dimensions from transplanting;", True)
    
    def get_plant_transplantings(self, plant_id):
        return self.execute_query(f"select id, date, width, height, radius, depth from transplanting where plant_id = {plant_id};", True)
    
    def get_harvests(self):
        return self.execute_query(f"select id, plant_id, date, yield from harvest;", True)
    
    def get_plant_harvests(self, plant_id):
        return self.execute_query(f"select id, plant_id, date, yield from harvest where plant_id = {plant_id};", True)

    def get_damages(self):
        return self.execute_query(f"select id, plant_id, damage_type_id, date from damage;", True)
    
    def get_plant_damages(self, plant_id):
        return self.execute_query(f"select id, plant_id, damage_type_id, date from damage where plant_id = {plant_id};", True)
        
    def get_training_types(self):
        return self.execute_query(f"select id, name, description from training_type;", True)
    
    def get_photoperiods(self):
        return self.execute_query(f"select id, name, description from photoperiod;", True)
    
    def get_genders(self):
        return self.execute_query(f"select id, name, description from gender;", True)
    
    def get_damage_types(self):
        return self.execute_query(f"select id, name, description from damage_type;", True)

    
    
    

    

