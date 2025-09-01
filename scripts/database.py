import mysql.connector
import datetime

class Database():

    def __init__(self, host, db_name, db_user, db_password):

        self.connection = mysql.connector.connect(
            host=host,
            user=db_user,
            password=db_password,
            database=db_name
        )

        self.query = self.connection.cursor(buffered=True)

        # 1) Tabelas de referência
        self.query.execute("""
        CREATE TABLE IF NOT EXISTS photoperiod (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) UNIQUE,
            description VARCHAR(500)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS gender (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) UNIQUE,
            description VARCHAR(500)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS intensity (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) UNIQUE,
            description VARCHAR(500)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS training_type (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) UNIQUE,
            description VARCHAR(500)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS damage_type (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) UNIQUE,
            description VARCHAR(500)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS sensor_type (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) UNIQUE,
            description VARCHAR(500)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS effector_type (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) UNIQUE,
            description VARCHAR(500)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(300) UNIQUE,
            password VARCHAR(64),
            is_admin TINYINT(1) DEFAULT 0
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.connection.commit()

        # 2) Tabelas principais
        self.query.execute("""
        CREATE TABLE IF NOT EXISTS grow (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(50) NOT NULL,
            lenght FLOAT,
            width FLOAT,
            height FLOAT,
            CONSTRAINT fk_grow_user FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS sensor (
            id INT AUTO_INCREMENT PRIMARY KEY,
            grow_id INT NOT NULL,
            ip VARCHAR(20),
            name VARCHAR(50) NOT NULL,
            sensor_type_id INT NOT NULL,
            last_sensor_value FLOAT NOT NULL DEFAULT 0,
            CONSTRAINT fk_sensor_grow FOREIGN KEY (grow_id) REFERENCES grow(id) ON DELETE CASCADE,
            CONSTRAINT fk_sensor_type FOREIGN KEY (sensor_type_id) REFERENCES sensor_type(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        self.query.execute("""
        CREATE TABLE IF NOT EXISTS effector (
            id INT AUTO_INCREMENT PRIMARY KEY,
            grow_id INT NOT NULL,
            effector_type_id INT NOT NULL,
            name VARCHAR(50) NOT NULL,
            ip VARCHAR(20),
            normal_on TINYINT(1) DEFAULT 0,
            power_on TINYINT(1) DEFAULT 0,
            scheduled TINYINT(1) DEFAULT 0,
            on_time TIME,
            off_time TIME,
            bounded TINYINT(1) DEFAULT 0,
            bounded_sensor_id INT NULL,
            threshold FLOAT,
            CONSTRAINT fk_effector_type FOREIGN KEY (effector_type_id) REFERENCES effector_type(id),
            CONSTRAINT fk_effector_sensor FOREIGN KEY (bounded_sensor_id) REFERENCES sensor(id),
            CONSTRAINT fk_effector_grow FOREIGN KEY (grow_id) REFERENCES grow(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sensor_id INT NOT NULL,
            value FLOAT NOT NULL,
            datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_sensordata_sensor FOREIGN KEY (sensor_id) REFERENCES sensor(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS plant (
            id INT AUTO_INCREMENT PRIMARY KEY,
            grow_id INT NOT NULL,
            name VARCHAR(50) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            photoperiod_id INT NOT NULL,
            gender_id INT NOT NULL,
            harvested TINYINT(1) DEFAULT 0,
            yield FLOAT DEFAULT 0,
            CONSTRAINT fk_plant_grow FOREIGN KEY (grow_id) REFERENCES grow(id) ON DELETE CASCADE,
            CONSTRAINT fk_plant_photoperiod FOREIGN KEY (photoperiod_id) REFERENCES photoperiod(id),
            CONSTRAINT fk_plant_gender FOREIGN KEY (gender_id) REFERENCES gender(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS training (
            id INT AUTO_INCREMENT PRIMARY KEY,
            plant_id INT NOT NULL,
            date DATE NOT NULL,
            training_type_id INT NOT NULL,
            CONSTRAINT fk_training_plant FOREIGN KEY (plant_id) REFERENCES plant(id),
            CONSTRAINT fk_training_type FOREIGN KEY (training_type_id) REFERENCES training_type(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS watering (
            id INT AUTO_INCREMENT PRIMARY KEY,
            plant_id INT NOT NULL,
            date DATE NOT NULL,
            mililiter INT NOT NULL,
            CONSTRAINT fk_watering_plant FOREIGN KEY (plant_id) REFERENCES plant(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS feeding (
            id INT AUTO_INCREMENT PRIMARY KEY,
            plant_id INT NOT NULL,
            date DATE NOT NULL,
            dosage INT NOT NULL,
            nitrogen INT NOT NULL,
            phosphorus INT NOT NULL,
            potassium INT NOT NULL,
            concentration INT NOT NULL,
            CONSTRAINT fk_feeding_plant FOREIGN KEY (plant_id) REFERENCES plant(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS transplanting (
            id INT AUTO_INCREMENT PRIMARY KEY,
            plant_id INT NOT NULL,
            date DATE NOT NULL,
            lenght FLOAT DEFAULT 0,
            width FLOAT DEFAULT 0,
            height FLOAT DEFAULT 0,
            radius FLOAT DEFAULT 0,
            CONSTRAINT fk_transplanting_plant FOREIGN KEY (plant_id) REFERENCES plant(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.query.execute("""
        CREATE TABLE IF NOT EXISTS damage (
            id INT AUTO_INCREMENT PRIMARY KEY,
            plant_id INT NOT NULL,
            date DATE NOT NULL,
            damage_type_id INT NOT NULL,
            intensity_id INT NOT NULL,
            CONSTRAINT fk_damage_plant FOREIGN KEY (plant_id) REFERENCES plant(id),
            CONSTRAINT fk_damage_type FOREIGN KEY (damage_type_id) REFERENCES damage_type(id),
            CONSTRAINT fk_damage_intensity FOREIGN KEY (intensity_id) REFERENCES intensity(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        self.connection.commit()

        # =========================
        # 3) Inserts iniciais
        # =========================
        inserts_sql = [
            "INSERT IGNORE INTO gender (name, description) VALUES ('Male',''),('Female',''),('Hermaphrodite',''),('Unknown','');",
            "INSERT IGNORE INTO photoperiod (name, description) VALUES ('Germination',''),('Seedling',''),('Vegetative',''),('Flowering',''),('Autoflower','');",
            "INSERT IGNORE INTO training_type (name, description) VALUES ('Low Stress Training',''),('High Stress Training',''),('Apical Pruning',''),('Lollipop Pruning',''),('FIM Pruning','');",
            "INSERT IGNORE INTO damage_type (name, description) VALUES ('Physical Damage',''),('Light Burning',''),('Wind Burning',''),('Overwatering',''),('Overfeeding',''),('Low watering',''),('Low Light',''),('Mold',''),('Parasites','');",
            "INSERT IGNORE INTO intensity (name, description) VALUES ('Very Low',''),('Low',''),('Medium',''),('High',''),('Very High','');",
            "INSERT IGNORE INTO sensor_type (name, description) VALUES ('Air Temperature',''),('Air Humidity',''),('Soil Temperature',''),('Soil Humidity',''),('Soil HP',''),('Water HP',''),('PPFD','');",
            "INSERT IGNORE INTO effector_type (name, description) VALUES ('Fan',''),('Lights',''),('Water Supplier',''),('Exhauster',''),('Blower',''),('Humidifier',''),('Dehumidifier','');",
            "INSERT IGNORE INTO user (email, password, is_admin) VALUES ('root@root.com','root',1),('user@user.com','user',0);"
        ]

        for stmt in inserts_sql:
            self.query.execute(stmt)
        self.connection.commit()

    def execute_query(self, query):
        print(f'{datetime.datetime.now()} - {query}')
        self.query.execute(query)
        self.connection.commit()

        retrieved_values = self.query.fetchall()  

        if retrieved_values:
            print(f'{datetime.datetime.now()} - {retrieved_values}')
            return retrieved_values
        else:
            return []
        
    def user_exists(self, email: str, password: str) -> bool:

        self.query.execute(f"SELECT * FROM user WHERE email='{email}' AND password='{password}'")

        account = self.query.fetchone()

        if not account:
            return False
        
        return True
    def get_user_id(self, email: str, password: str):
        self.query.execute(f"SELECT id FROM user WHERE email='{email}' AND password='{password}';")
        user_id = self.query.fetchone()
        if user_id:   
            return user_id[0]
        else:
            return str(0)
        
    def get_admin(self, user_id):
        self.query.execute(f"SELECT is_admin FROM user WHERE id={user_id};")
        is_admin = self.query.fetchone()

        if int(is_admin[0]) == 0:
            return False
        
        return True
    def insert_user(self, email: str, password: str, is_admin: str) -> bool:
        self.query.execute(f"INSERT OR IGNORE INTO user(email, password, is_admin) values ('{email}', '{password}', {is_admin});")
        self.connection.commit()
        return True
    
    def get_user_email(self, user_id: int) -> str:
        self.query.execute(f"SELECT email FROM user WHERE id={user_id}")
        email = self.query.fetchone()
        if email:
            return email[0]
        else:
            return ""
        
    def get_user_password(self, user_id: int) -> str:
        self.query.execute(f"SELECT password FROM user WHERE id={user_id}")
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
        self.query.execute(f"UPDATE user SET password = '{password}' WHERE id={user_id}")
        self.connection.commit()
    def alter_email(self, user_id, email):
        self.query.execute(f"UPDATE user SET email = '{email}' WHERE id={user_id}")
        self.connection.commit()
    def delete_user(self, id):
        self.query.execute(f"DELETE FROM user WHERE id={id};")
        self.connection.commit()
    def update_user(self, user_id, email, password, is_admin):
        self.query.execute(f"UPDATE user SET email = '{email}', password = '{password}', is_admin = {is_admin} WHERE id={user_id};")
        self.connection.commit()
    ##################################################################################################
    def get_plants(self):
        return self.execute_query(f"select id, grow_id, name, start_date, end_date, photoperiod_id, gender_id, harvested, yield from plant;")
    def insert_plant(self, grow_id, name, date, photoperiod_id, gender_id):
        self.execute_query(f"insert into plant (grow_id, name, start_date, photoperiod_id, gender_id) values ({grow_id}, '{name}', DATE('{date}'), {photoperiod_id}, {gender_id});")
    def update_plant(self, id, name, date, photoperiod_id, gender_id, harvested=0):
        self.execute_query(f"update plant set name = '{name}', start_date = DATE('{date}'), harvested = {harvested}, photoperiod_id = {photoperiod_id}, gender_id = {gender_id} where id = {id};")
    def get_plant(self, plant_id):
        return self.execute_query(f"select id, grow_id, name, start_date, end_date, photoperiod_id, gender_id, harvested, yield from plant where id = {plant_id};")
    def delete_plant(self, plant_id):
        return self.execute_query(f"delete from plant where id = {plant_id};")
    ##################################################################################################
    def get_trainings(self):
        return self.execute_query(f"select id, plant_id, training_type_id, date from training;")
    def get_plant_trainings(self, plant_id):
        return self.execute_query(f"select id, plant_id, training_type_id, date from training where plant_id = {plant_id};")
    def insert_training(self, plant_id, training_type_id, date):
        self.execute_query(f"insert into training (plant_id, training_type_id, date) values {plant_id}, {training_type_id}, DATE('{date}');")
    ##################################################################################################
    def get_waterings(self):
        return self.execute_query(f"select id, plant_id, date, mililiter from watering;")
    def get_plant_waterings(self, plant_id):
        return self.execute_query(f"select id, date, mililiter from watering where plant_id = {plant_id};")
    def insert_watering(self, plant_id, date, mililiter):
        self.execute_query(f"insert into watering (plant_id, date, mililiter) values ({plant_id}, DATE('{date}'), {mililiter});")
    def delete_watering(self, watering_id):
        return self.execute_query(f"delete from watering where id = {watering_id};")
    ##################################################################################################
    def get_feedings(self):
        return self.execute_query(f"select id, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium from feeding;")
    def get_plant_feedings(self, plant_id):
        return self.execute_query(f"select id, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium from feeding where plant_id = {plant_id};")
    def get_plant_feedings(self, plant_id):
        return self.execute_query(f"select id, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium from feeding where plant_id = {plant_id};")
    def insert_feeding(self, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium):
        self.execute_query(f"insert into watering (plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium) values {plant_id}, DATE('{date}'), {dosage}, {concentration}, {nitrogen}, {phosphorus}, {potassium};")
    ##################################################################################################
    def get_transplantings(self):
        return self.execute_query(f"select id, plant_id, date, lenght, width, height, radius from transplanting;")
    def get_plant_transplantings(self, plant_id):
        return self.execute_query(f"select id, plant_id, date, lenght, width, height, radius from transplanting where plant_id = {plant_id};")
    ##################################################################################################
    def get_damages(self):
        return self.execute_query(f"select id, plant_id, damage_type_id, date, intensity_id from damage;")
    def get_plant_damages(self, plant_id):
        return self.execute_query(f"select id, plant_id, damage_type_id, date, intensity_id from damage where plant_id = {plant_id};")
    ##################################################################################################
    def get_training_types(self):
        return self.execute_query(f"select id, name, description from training_type;")
    
    def get_photoperiods(self):
        return self.execute_query(f"select id, name, description from photoperiod;")
    
    def get_genders(self):
        return self.execute_query(f"select id, name, description from gender;")
    
    def get_damage_types(self):
        return self.execute_query(f"select id, name, description from damage_type;")
    
    def get_intensities(self):
        return self.execute_query(f"select id, name, description from intensity;")
    
    def get_device_types(self):
        return self.execute_query(f"select id, name, description from device_type;")
    
    def insert_grow(self, user_id, name,  lenght, width, height):
        self.query.execute(f"INSERT INTO grow(user_id, name, lenght, width, height) values ({user_id}, '{name}', {lenght}, {width}, {height});")
        self.connection.commit()
        return True
    
    def get_user_grows(self, user_id):
        return self.execute_query(f"select id, user_id, name, lenght, width, height from grow where user_id = {user_id};")
    
    def get_grow(self, grow_id):
        return self.execute_query(f"select id, user_id, name, lenght, width, height from grow where id = {grow_id};")
    
    def get_grow_plants(self, grow_id):
        return self.execute_query(f"select id, grow_id, name, start_date, end_date, photoperiod_id, gender_id, harvested, yield from plant where grow_id = {grow_id};")
    
    def get_grow_devices(self, grow_id):
        return self.execute_query(f"select id, grow_id, device_type_id, name, normal_on, power_on, sensor_type_id, scheduled, on_time, off_time, bounded, bounded_sensor_type_id, bounded_device_id, threshold, ip from device where id = {grow_id};")
    
    def insert_device(self, grow_id, device_type_id, name):
        return self.execute_query(f"insert into device (grow_id, device_type_id, name) VALUES ({grow_id}, {device_type_id}, '{name}');")
    
    def delete_grow(self, grow_id):
        return self.execute_query(f"delete from grow where id = {grow_id};")
    
    def get_sensor_types(self):
        return self.execute_query(f"select id, name, description from sensor_type;")
    
    def get_effector_types(self):
        return self.execute_query(f"select id, name, description from effector_type;")

    def get_grow_sensors(self, grow_id):
        return self.execute_query(f"select id, grow_id, ip, name, sensor_type_id, last_sensor_value from sensor where grow_id = {grow_id};")
    
    def get_grow_effectors(self, grow_id):
        return self.execute_query(f"select id, grow_id, effector_type_id, name, ip, normal_on, power_on, scheduled, on_time, off_time, bounded, bounded_sensor_id, threshold from effector where grow_id = {grow_id};")
    
    def insert_sensor_data(self, sensor_id, value):
        self.execute_query(f"INSERT INTO sensor_data (sensor_id, value) VALUES ({sensor_id}, {value});")
        # Atualiza last_sensor_value manualmente
        self.execute_query(f"UPDATE sensor SET last_sensor_value = {value} WHERE id = {sensor_id};")
        # Remove dados antigos
        self.execute_query(f"DELETE FROM sensor_data WHERE sensor_id = {sensor_id} AND datetime < NOW() - INTERVAL 1 DAY;")

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
        return self.execute_query(f"select id, grow_id, effector_type_id, name, ip, normal_on, power_on, scheduled, on_time, off_time, bounded, bounded_sensor_id, threshold from effector where id = {effector_id};")
    
    def get_last_sensor_data_value(self, sensor_id):
        return self.execute_query(f"select last_sensor_value from sensor where id = {sensor_id};")
    
    def set_effector_power_on(self, effector_id, power_on):
        self.execute_query(f"update effector set power_on = {power_on} where id = {effector_id};")

    def update_effector(self, effector_id, name, effector_type_id, ip, normal_on, scheduled, on_time, off_time, bounded, bounded_sensor_id, threshold):
        sql = f"""
        UPDATE effector
        SET effector_type_id = {effector_type_id},
            name = '{name}',
            ip = '{ip}',
            normal_on = {normal_on},
            scheduled = {scheduled},
            bounded = {bounded},
            bounded_sensor_id = {bounded_sensor_id},
            threshold = {threshold},
            on_time = {f"TIME('{on_time}')" if on_time else 'NULL'},
            off_time = {f"TIME('{off_time}')" if off_time else 'NULL'}
        WHERE id = {effector_id};
        """
        self.execute_query(sql)
