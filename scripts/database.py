import sqlite3

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

        print(query)
        self.query.execute(query)
        self.connection.commit()

        retrieved_values = None

        if fetch:
            retrieved_values = self.query.fetchall()  

            if retrieved_values:
                return retrieved_values
            else:
                return None
        else:
            return retrieved_values
        
    def get_plants(self):
        return self.execute_query(f"select id, name, date, photoperiod_id from plant;", True)
    
    def insert_plant(self, name, planting_date, photoperiod_id):
        self.execute_query(f"insert into plant (name, date, photoperiod_id) values '{name}', DATE('{planting_date}'), {photoperiod_id};")

    def get_trainings(self):
        return self.execute_query(f"select id, plant_id, training_type_id, date from training;", True)
    
    def insert_training(self, plant_id, training_type_id, date):
        self.execute_query(f"insert into training (plant_id, training_type_id, date) values {plant_id}, {training_type_id}, DATE('{date}');")
    
    def get_waterings(self):
        return self.execute_query(f"select id, plant_id, date, mililiter from watering;", True)
    
    def insert_watering(self, plant_id, date, mililiter):
        self.execute_query(f"insert into watering (plant_id, date, mililiter) values {plant_id}, DATETIME('{date}'), {mililiter};")
    
    def get_feedings(self):
        return self.execute_query(f"select id, plant_id, date, dose, concentration, nitrogen, phosphorus, potassium from feeding;", True)
    
    def insert_feeding(self, plant_id, date, dose, concentration, nitrogen, phosphorus, potassium):
        self.execute_query(f"insert into watering (plant_id, date, dose, concentration, nitrogen, phosphorus, potassium) values {plant_id}, DATE('{date}'), {dose}, {concentration}, {nitrogen}, {phosphorus}, {potassium};")
    
    def get_training_types(self):
        return self.execute_query(f"select id, name, description from training_type;", True)
    
    def get_photoperiods(self):
        return self.execute_query(f"select id, name, description from photoperiod;", True)
    
    
    

    

