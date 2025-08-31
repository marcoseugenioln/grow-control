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
                print(f'{datetime.datetime.now()} - {retrieved_values}')
                return retrieved_values
            else:
                return []
        else:
            return retrieved_values
    def insert_measurement(self, device_id, sensor_type_id, value):
        # insert measurement into database
        self.query.execute(f"INSERT OR IGNORE INTO measurement(device_id, sensor_type_id, value) values ({device_id}, {sensor_type_id}, {value});")
        self.connection.commit()
        return True
    def user_exists(self, email: str, password: str) -> bool:

        self.query.execute(f"SELECT * FROM user WHERE email == '{email}' AND password == '{password}'")

        account = self.query.fetchone()

        if not account:
            return False
        
        return True
    def get_user_id(self, email: str, password: str):
        self.query.execute(f"SELECT id FROM user WHERE email == '{email}' AND password == '{password}';")
        user_id = self.query.fetchone()
        if user_id:   
            return user_id[0]
        else:
            return str(0)
    def get_admin(self, user_id):
        self.query.execute(f"SELECT is_admin FROM user WHERE id == {user_id};")
        is_admin = self.query.fetchone()

        if int(is_admin[0]) == 0:
            return False
        
        return True
    def insert_user(self, email: str, password: str, is_admin: str) -> bool:
        self.query.execute(f"INSERT OR IGNORE INTO user(email, password, is_admin) values ('{email}', '{password}', {is_admin});")
        self.connection.commit()
        return True
    def get_user_email(self, user_id: int) -> str:
        self.query.execute(f"SELECT email FROM user WHERE id == {user_id}")
        email = self.query.fetchone()
        if email:
            return email[0]
        else:
            return ""
    def get_user_password(self, user_id: int) -> str:
        self.query.execute(f"SELECT password FROM user WHERE id == {user_id}")
        password = self.query.fetchone()
        if password:
            return password[0]
        else:
            return ""
    def get_users(self):
        self.query.execute(f"SELECT id, email, password FROM user")
        users = self.query.fetchall()        
        return users
    def alter_password(self, user_id, password):
        self.query.execute(f"UPDATE user SET password = '{password}' WHERE id == {user_id}")
        self.connection.commit()
    def alter_email(self, user_id, email):
        self.query.execute(f"UPDATE user SET email = '{email}' WHERE id == {user_id}")
        self.connection.commit()
    def delete_user(self, id):
        self.query.execute(f"DELETE FROM user WHERE id == {id};")
        self.connection.commit()
    def update_user(self, user_id, email, password, is_admin):
        self.query.execute(f"UPDATE user SET email = '{email}', password = '{password}', is_admin = {is_admin} WHERE id == {user_id};")
        self.connection.commit()
    ##################################################################################################
    def get_plants(self):
        return self.execute_query(f"select id, grow_id, name, start_date, end_date, photoperiod_id, gender_id, harvested, yield from plant;", True)
    def insert_plant(self, grow_id, name, date, photoperiod_id, gender_id):
        self.execute_query(f"insert into plant (grow_id, name, start_date, photoperiod_id, gender_id) values ({grow_id}, '{name}', DATE('{date}'), {photoperiod_id}, {gender_id});")
    def update_plant(self, id, name, date, photoperiod_id, gender_id, harvested=0):
        self.execute_query(f"update plant set name = '{name}', start_date = DATE('{date}'), harvested = {harvested}, photoperiod_id = {photoperiod_id}, gender_id = {gender_id} where id = {id};")
    def get_plant(self, plant_id):
        return self.execute_query(f"select id, grow_id, name, start_date, end_date, photoperiod_id, gender_id, harvested, yield from plant where id = {plant_id};", True)
    def delete_plant(self, plant_id):
        return self.execute_query(f"delete from plant where id = {plant_id};")
    ##################################################################################################
    def get_trainings(self):
        return self.execute_query(f"select id, plant_id, training_type_id, date from training;", True)
    def get_plant_trainings(self, plant_id):
        return self.execute_query(f"select id, plant_id, training_type_id, date from training where plant_id = {plant_id};", True)
    def insert_training(self, plant_id, training_type_id, date):
        self.execute_query(f"insert into training (plant_id, training_type_id, date) values {plant_id}, {training_type_id}, DATE('{date}');")
    ##################################################################################################
    def get_waterings(self):
        return self.execute_query(f"select id, plant_id, date, mililiter from watering;", True)
    def get_plant_waterings(self, plant_id):
        return self.execute_query(f"select id, date, mililiter from watering where plant_id = {plant_id};", True)
    def insert_watering(self, plant_id, date, mililiter):
        self.execute_query(f"insert into watering (plant_id, date, mililiter) values ({plant_id}, DATE('{date}'), {mililiter});")
    def delete_watering(self, watering_id):
        return self.execute_query(f"delete from watering where id = {watering_id};")
    ##################################################################################################
    def get_feedings(self):
        return self.execute_query(f"select id, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium from feeding;", True)
    def get_plant_feedings(self, plant_id):
        return self.execute_query(f"select id, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium from feeding where plant_id = {plant_id};", True)
    def get_plant_feedings(self, plant_id):
        return self.execute_query(f"select id, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium from feeding where plant_id = {plant_id};", True)
    def insert_feeding(self, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium):
        self.execute_query(f"insert into watering (plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium) values {plant_id}, DATE('{date}'), {dosage}, {concentration}, {nitrogen}, {phosphorus}, {potassium};")
    ##################################################################################################
    def get_transplantings(self):
        return self.execute_query(f"select id, plant_id, date, lenght, width, height, radius from transplanting;", True)
    def get_plant_transplantings(self, plant_id):
        return self.execute_query(f"select id, plant_id, date, lenght, width, height, radius from transplanting where plant_id = {plant_id};", True)
    ##################################################################################################
    def get_damages(self):
        return self.execute_query(f"select id, plant_id, damage_type_id, date, intensity_id from damage;", True)
    def get_plant_damages(self, plant_id):
        return self.execute_query(f"select id, plant_id, damage_type_id, date, intensity_id from damage where plant_id = {plant_id};", True)
    ##################################################################################################
    def get_training_types(self):
        return self.execute_query(f"select id, name, description from training_type;", True)
    
    def get_photoperiods(self):
        return self.execute_query(f"select id, name, description from photoperiod;", True)
    
    def get_genders(self):
        return self.execute_query(f"select id, name, description from gender;", True)
    
    def get_damage_types(self):
        return self.execute_query(f"select id, name, description from damage_type;", True)
    
    def get_intensities(self):
        return self.execute_query(f"select id, name, description from intensity;", True)
    
    def get_device_types(self):
        return self.execute_query(f"select id, name, description from device_type;", True)
    
    def insert_grow(self, user_id, name,  lenght, width, height):
        self.query.execute(f"INSERT INTO grow(user_id, name, lenght, width, height) values ({user_id}, '{name}', {lenght}, {width}, {height});")
        self.connection.commit()
        return True
    
    def get_user_grows(self, user_id):
        return self.execute_query(f"select id, user_id, name, lenght, width, height from grow where user_id = {user_id};", True)
    
    def get_grow(self, grow_id):
        return self.execute_query(f"select id, user_id, name, lenght, width, height from grow where id = {grow_id};", True)
    
    def get_grow_plants(self, grow_id):
        return self.execute_query(f"select id, grow_id, name, start_date, end_date, photoperiod_id, gender_id, harvested, yield from plant where grow_id = {grow_id};", True)
    
    def get_grow_devices(self, grow_id):
        return self.execute_query(f"select id, grow_id, device_type_id, name, normal_on, power_on, sensor_type_id, scheduled, on_time, off_time, bounded, bounded_sensor_type_id, bounded_device_id, threshold, ip from device where id = {grow_id};", True)
    
    def insert_device(self, grow_id, device_type_id, name):
        return self.execute_query(f"insert into device (grow_id, device_type_id, name) VALUES ({grow_id}, {device_type_id}, '{name}');")
    
    def delete_grow(self, grow_id):
        return self.execute_query(f"delete from grow where id = {grow_id};")
    
    def get_sensor_types(self):
        return self.execute_query(f"select id, name, description from sensor_type;", True)
    
    def get_effector_types(self):
        return self.execute_query(f"select id, name, description from effector_type;", True)

    def get_grow_sensors(self, grow_id):
        return self.execute_query(f"select id, grow_id, ip, name, sensor_type_id, last_value from sensor where grow_id = {grow_id};", True)
    
    def get_grow_effectors(self, grow_id):
        return self.execute_query(f"select id, grow_id, effector_type_id, name, ip, normal_on, power_on, scheduled, on_time, off_time, bounded, bounded_sensor_id, threshold from effector where grow_id = {grow_id};", True)
    
    def insert_sensor(self, grow_id, name, sensor_type_id):
        self.execute_query(f"insert into sensor (grow_id, name, sensor_type_id) values ({grow_id}, '{name}', {sensor_type_id});")

    def update_sensor(self, sensor_id, name, sensor_type_id, ip):
        self.execute_query(f"update sensor set name = '{name}', ip = '{ip}', sensor_type_id = {sensor_type_id} where id = {sensor_id};")

    def delete_sensor(self, sensor_id):
        return self.execute_query(f"delete from sensor where id = {sensor_id};")
    
    def insert_effector(self, grow_id, effector_type_id, name):
        self.execute_query(f"insert into effector (grow_id, name, effector_type_id) values ({grow_id}, '{name}', {effector_type_id});")

    def delete_effector(self, effector_id):
        return self.execute_query(f"delete from effector where id = {effector_id};")
    
    def update_grow(self, grow_id, name, lenght, width, height):
        self.execute_query(f"update grow set name = '{name}', lenght = {lenght}, width = {width}, height = {height} where id = {grow_id};")

    def insert_sensor_data(self, sensor_id, value):
        self.execute_query(f"insert into sensor_data (sensor_id, value) values ({sensor_id}, {value});")

    def get_effector(self, effector_id):
        return self.execute_query(f"select id, grow_id, effector_type_id, name, ip, normal_on, power_on, scheduled, on_time, off_time, bounded, bounded_sensor_id, threshold from effector where id = {effector_id};", True)
    
    def get_last_sensor_data_value(self, sensor_id):
        return self.execute_query(f"select last_value from sensor where id = {sensor_id};", True)
    
    def set_effector_power_on(self, effector_id, power_on):
        self.execute_query(f"update effector set power_on = {power_on} where id = {effector_id};")

    def update_effector(self, effector_id, name, effector_type_id, ip, normal_on, scheduled, on_time, off_time, bounded, bounded_sensor_id, threshold):
        self.execute_query(f"update effector set effector_type_id = {effector_type_id}, name = '{name}', ip = '{ip}', normal_on = {normal_on}, scheduled = {scheduled}, on_time = TIME('{on_time}'), off_time = TIME('{off_time}'), bounded = {bounded}, bounded_sensor_id = {bounded_sensor_id}, threshold = {threshold} where id = {effector_id};")
