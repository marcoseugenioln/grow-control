from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort, jsonify
from flask import Flask
import logging
import mysql.connector
import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re

class Database():

    def __init__(self, host, db_name, db_user, db_password):
        self.host = host
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        
        self.connection = mysql.connector.connect(
                host=self.host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
                port=3306,
                buffered=True,
                ssl_disabled=True,
                autocommit=True,
                use_pure=True  # FORÇAR MODO PURO - resolve o erro bytearray
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
            password VARCHAR(255),
            is_admin TINYINT(1) DEFAULT 0
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
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
        # 3) Inserts iniciais
        inserts_sql = [
            "INSERT IGNORE INTO gender (name, description) VALUES ('Male',''),('Female',''),('Hermaphrodite',''),('Unknown','');",
            "INSERT IGNORE INTO photoperiod (name, description) VALUES ('Germination',''),('Seedling',''),('Vegetative',''),('Flowering',''),('Autoflower','');",
            "INSERT IGNORE INTO training_type (name, description) VALUES ('Low Stress Training',''),('High Stress Training',''),('Apical Pruning',''),('Lollipop Pruning',''),('FIM Pruning','');",
            "INSERT IGNORE INTO damage_type (name, description) VALUES ('Physical Damage',''),('Light Burning',''),('Wind Burning',''),('Overwatering',''),('Overfeeding',''),('Low watering',''),('Low Light',''),('Mold',''),('Parasites','');",
            "INSERT IGNORE INTO intensity (name, description) VALUES ('Very Low',''),('Low',''),('Medium',''),('High',''),('Very High','');",
            "INSERT IGNORE INTO sensor_type (name, description) VALUES ('Air Temperature',''),('Air Humidity',''),('Soil Temperature',''),('Soil Humidity',''),('Soil HP',''),('Water HP',''),('PPFD','');",
            "INSERT IGNORE INTO effector_type (name, description) VALUES ('Fan',''),('Lights',''),('Water Supplier',''),('Exhauster',''),('Blower',''),('Humidifier',''),('Dehumidifier','');"
        ]
        for stmt in inserts_sql:
            self.query.execute(stmt)

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
                port=3306,
                buffered=True,
                ssl_disabled=True,
                autocommit=True,
                use_pure=True  # FORÇAR MODO PURO - resolve o erro bytearray
            )
            self.query = self.connection.cursor(buffered=True)
        except Exception as e:
            raise

    def ensure_connection(self):
        try:
            self.connection.ping(reconnect=True, attempts=3, delay=5)
        except:
            self.connect()

    def execute_query(self, query, params=None):
        self.ensure_connection()
        
        try:
            self.query.execute(query, params or ())
            
            if self.query.description:
                retrieved_values = self.query.fetchall()
                return retrieved_values
            else:
                affected_rows = self.query.rowcount
                return affected_rows
                
        except Exception as e:
            print(f'{datetime.datetime.now()} - Erro: {e}')
            try:
                self.connect()
                self.query.execute(query, params or ())
                if self.query.description:
                    return self.query.fetchall()
                else:
                    return self.query.rowcount
            except Exception as retry_error:
                print(f'Retry failed: {retry_error}')
                raise
        
    def verify_password(self, email: str, password: str) -> bool:
        """Verifica se a senha está correta usando hash"""
        try:
            result = self.execute_query(
                "SELECT password FROM user WHERE email = %s",
                (email,)
            )
            if result and len(result) > 0:
                stored_hash = result[0][0]
                return check_password_hash(stored_hash, password)
            return False
        except Exception as e:
            print(f"Erro ao verificar senha: {e}")
            return False
    
    def get_user_id(self, email: str):
        """Obtém ID do usuário sem expor senha"""
        result = self.execute_query(
            "SELECT id FROM user WHERE email = %s",
            (email,)
        )
        return result[0][0] if result and len(result) > 0 else None
        
    def get_admin(self, user_id):
        is_admin = self.execute_query(
            "SELECT is_admin FROM user WHERE id = %s",
            (user_id,)
        )
        if len(is_admin) > 0:
            if int(is_admin[0][0]) == 0:
                return False
        return True
    
    def create_user(self, email: str, password: str, is_admin: bool = False) -> bool:
        """Cria usuário com senha hasheada"""
        hashed_password = generate_password_hash(password)
        try:
            self.execute_query(
                "INSERT INTO user (email, password, is_admin) VALUES (%s, %s, %s)",
                (email, hashed_password, is_admin)
            )
            return True
        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            return False
    
    def get_user_email(self, user_id: int) -> str:
        email = self.execute_query(
            "SELECT email FROM user WHERE id = %s",
            (user_id,)
        )
        return email[0][0] if email and len(email) > 0 else ""
        
    def get_users(self):
        return self.execute_query("SELECT id, email, is_admin FROM user")
    
    def alter_password(self, user_id, password):
        hashed_password = generate_password_hash(password)
        self.execute_query(
            "UPDATE user SET password = %s WHERE id = %s",
            (hashed_password, user_id)
        )
    
    def alter_email(self, user_id, email):
        self.execute_query(
            "UPDATE user SET email = %s WHERE id = %s",
            (email, user_id)
        )
    
    def delete_user(self, id):
        self.execute_query("DELETE FROM user WHERE id = %s", (id,))
    
    def update_user(self, user_id, email, password, is_admin):
        hashed_password = generate_password_hash(password)
        self.execute_query(
            "UPDATE user SET email = %s, password = %s, is_admin = %s WHERE id = %s",
            (email, hashed_password, is_admin, user_id)
        )
    
    def get_plants(self):
        return self.execute_query("SELECT id, grow_id, name, start_date, end_date, photoperiod_id, gender_id, harvested, yield FROM plant")
    
    def insert_plant(self, grow_id, name, date, photoperiod_id, gender_id):
        self.execute_query(
            "INSERT INTO plant (grow_id, name, start_date, photoperiod_id, gender_id) VALUES (%s, %s, DATE(%s), %s, %s)",
            (grow_id, name, date, photoperiod_id, gender_id)
        )
    
    def update_plant(self, id, name, date, photoperiod_id, gender_id, harvested=0):
        self.execute_query(
            "UPDATE plant SET name = %s, start_date = DATE(%s), harvested = %s, photoperiod_id = %s, gender_id = %s WHERE id = %s",
            (name, date, harvested, photoperiod_id, gender_id, id)
        )
    
    def get_plant(self, plant_id):
        return self.execute_query(
            "SELECT id, grow_id, name, start_date, end_date, photoperiod_id, gender_id, harvested, yield FROM plant WHERE id = %s",
            (plant_id,)
        )
    
    def delete_plant(self, plant_id):
        return self.execute_query("DELETE FROM plant WHERE id = %s", (plant_id,))
    
    def get_trainings(self):
        return self.execute_query("SELECT id, plant_id, training_type_id, date FROM training")
    
    def get_plant_trainings(self, plant_id):
        return self.execute_query(
            "SELECT id, plant_id, training_type_id, date FROM training WHERE plant_id = %s",
            (plant_id,)
        )
    
    def insert_training(self, plant_id, training_type_id, date):
        self.execute_query(
            "INSERT INTO training (plant_id, training_type_id, date) VALUES (%s, %s, DATE(%s))",
            (plant_id, training_type_id, date)
        )
    
    def get_waterings(self):
        return self.execute_query("SELECT id, plant_id, date, mililiter FROM watering")
    
    def get_plant_waterings(self, plant_id):
        return self.execute_query(
            "SELECT id, date, mililiter FROM watering WHERE plant_id = %s",
            (plant_id,)
        )
    
    def insert_watering(self, plant_id, date, mililiter):
        self.execute_query(
            "INSERT INTO watering (plant_id, date, mililiter) VALUES (%s, DATE(%s), %s)",
            (plant_id, date, mililiter)
        )
    
    def delete_watering(self, watering_id):
        return self.execute_query("DELETE FROM watering WHERE id = %s", (watering_id,))

    def get_feedings(self):
        return self.execute_query("SELECT id, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium FROM feeding")

    def get_plant_feedings(self, plant_id):
        return self.execute_query(
            "SELECT id, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium FROM feeding WHERE plant_id = %s",
            (plant_id,)
        )

    def insert_feeding(self, plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium):
        self.execute_query(
            "INSERT INTO feeding (plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium) VALUES (%s, DATE(%s), %s, %s, %s, %s, %s)",
            (plant_id, date, dosage, concentration, nitrogen, phosphorus, potassium)
        )

    def get_transplantings(self):
        return self.execute_query("SELECT id, plant_id, date, lenght, width, height, radius FROM transplanting")
    
    def get_plant_transplantings(self, plant_id):
        return self.execute_query(
            "SELECT id, plant_id, date, lenght, width, height, radius FROM transplanting WHERE plant_id = %s",
            (plant_id,)
        )
    
    def get_damages(self):
        return self.execute_query("SELECT id, plant_id, damage_type_id, date, intensity_id FROM damage")
    
    def get_plant_damages(self, plant_id):
        return self.execute_query(
            "SELECT id, plant_id, damage_type_id, date, intensity_id FROM damage WHERE plant_id = %s",
            (plant_id,)
        )
    
    def get_training_types(self):
        return self.execute_query("SELECT id, name, description FROM training_type")
    
    def get_photoperiods(self):
        return self.execute_query("SELECT id, name, description FROM photoperiod")
    
    def get_genders(self):
        return self.execute_query("SELECT id, name, description FROM gender")
    
    def get_damage_types(self):
        return self.execute_query("SELECT id, name, description FROM damage_type")
    
    def get_intensities(self):
        return self.execute_query("SELECT id, name, description FROM intensity")
    
    def insert_grow(self, user_id, name, lenght, width, height):
        self.execute_query(
            "INSERT INTO grow(user_id, name, lenght, width, height) VALUES (%s, %s, %s, %s, %s)",
            (user_id, name, lenght, width, height)
        )
        return True
    
    def get_user_grows(self, user_id):
        return self.execute_query(
            "SELECT id, user_id, name, lenght, width, height FROM grow WHERE user_id = %s",
            (user_id,)
        )
    
    def get_grow(self, grow_id):
        return self.execute_query(
            "SELECT id, user_id, name, lenght, width, height FROM grow WHERE id = %s",
            (grow_id,)
        )
    
    def get_grow_plants(self, grow_id):
        return self.execute_query(
            "SELECT id, grow_id, name, start_date, end_date, photoperiod_id, gender_id, harvested, yield FROM plant WHERE grow_id = %s",
            (grow_id,)
        )
    
    def get_sensor_types(self):
        return self.execute_query("SELECT id, name, description FROM sensor_type")
    
    def get_effector_types(self):
        return self.execute_query("SELECT id, name, description FROM effector_type")
    
    def get_grow_sensors(self, grow_id):
        return self.execute_query(
            "SELECT id, grow_id, ip, name, sensor_type_id, last_sensor_value FROM sensor WHERE grow_id = %s",
            (grow_id,)
        )
    
    def get_grow_effectors(self, grow_id):
        query = """
                SELECT 
                    id, 
                    grow_id, 
                    effector_type_id, 
                    name, 
                    ip, 
                    normal_on, 
                    power_on, 
                    scheduled, 
                    DATE_FORMAT(on_time, '%H:%i') as on_time,
                    DATE_FORMAT(off_time, '%H:%i') as off_time,
                    bounded, 
                    bounded_sensor_id, 
                    threshold 
                FROM effector 
                WHERE grow_id = %s
                """
        return self.execute_query(query, (grow_id,))
    
    def insert_sensor_data(self, sensor_id, value):
        self.execute_query(
            "INSERT INTO sensor_data (sensor_id, value) VALUES (%s, %s)",
            (sensor_id, value)
        )
        self.execute_query(
            "UPDATE sensor SET last_sensor_value = %s WHERE id = %s",
            (value, sensor_id)
        )
        self.execute_query(
            "DELETE FROM sensor_data WHERE sensor_id = %s AND datetime < NOW() - INTERVAL 1 DAY",
            (sensor_id,)
        )
    
    def update_sensor(self, sensor_id, name, sensor_type_id, ip):
        self.execute_query(
            "UPDATE sensor SET name = %s, ip = %s, sensor_type_id = %s WHERE id = %s",
            (name, ip, sensor_type_id, sensor_id)
        )
    
    def delete_sensor(self, sensor_id):
        return self.execute_query("DELETE FROM sensor WHERE id = %s", (sensor_id,))
    
    def insert_effector(self, grow_id, effector_type_id, name):
        self.execute_query(
            "INSERT INTO effector (grow_id, name, effector_type_id) VALUES (%s, %s, %s)",
            (grow_id, name, effector_type_id)
        )
    
    def delete_effector(self, effector_id):
        return self.execute_query("DELETE FROM effector WHERE id = %s", (effector_id,))
    
    def update_grow(self, grow_id, name, lenght, width, height):
        self.execute_query(
            "UPDATE grow SET name = %s, lenght = %s, width = %s, height = %s WHERE id = %s",
            (name, lenght, width, height, grow_id)
        )
    
    def insert_sensor(self, grow_id, name, sensor_type_id):
        self.execute_query(
            "INSERT INTO sensor (grow_id, name, sensor_type_id) VALUES (%s, %s, %s)",
            (grow_id, name, sensor_type_id)
        )
    
    def get_effector(self, effector_id):
        return self.execute_query(
            "SELECT id, grow_id, effector_type_id, name, ip, normal_on, power_on, scheduled, on_time, off_time, bounded, bounded_sensor_id, threshold FROM effector WHERE id = %s",
            (effector_id,)
        )
    
    def get_last_sensor_data_value(self, sensor_id):
        return self.execute_query(
            "SELECT last_sensor_value FROM sensor WHERE id = %s",
            (sensor_id,)
        )
    
    def set_effector_power_on(self, effector_id, power_on):
        self.execute_query(
            "UPDATE effector SET power_on = %s WHERE id = %s",
            (power_on, effector_id)
        )
    
    def update_effector(self, effector_id, name, effector_type_id, ip, normal_on, scheduled, on_time, off_time, bounded, bounded_sensor_id, threshold):
        sql = """
        UPDATE effector
        SET effector_type_id = %s,
            name = %s,
            ip = %s,
            normal_on = %s,
            scheduled = %s,
            bounded = %s,
            bounded_sensor_id = %s,
            threshold = %s,
            on_time = %s,
            off_time = %s
        WHERE id = %s
        """
        bounded_sensor_val = bounded_sensor_id if int(bounded_sensor_id) > 0 else None
        on_time_val = on_time if on_time else None
        off_time_val = off_time if off_time else None
        
        self.execute_query(sql, (
            effector_type_id, name, ip, normal_on, scheduled, bounded, 
            bounded_sensor_val, threshold, on_time_val, off_time_val, effector_id
        ))

# Funções auxiliares de validação
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_strong_password(password):
    if len(password) < 8:
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    return True

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key-change-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # True apenas em produção com HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

site = Blueprint('site', __name__, template_folder='templates')

db_host = os.environ.get('DB_HOST', 'localhost')
db_name = os.environ.get('DB_NAME', 'growcontrol')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'root')

database = Database(db_host, db_name, db_user, db_password)

@app.errorhandler(Exception)
def handle_exception(e):
    return f"Ocorreu um erro interno: {e}", 500

@app.route("/")
def index():
    if 'logged_in' not in session or session['logged_in'] != True:
        return redirect(url_for('login'))
    
    grows = database.get_user_grows(session['user_id'])

    grow_plants = {}
    for grow in grows:
        grow_plants[grow[0]] = database.get_grow_plants(grow[0])

    grow_sensors = {}
    for grow in grows:
        grow_sensors[grow[0]] = database.get_grow_sensors(grow[0])

    grow_effectors = {}
    for grow in grows:
        grow_effectors[grow[0]] = database.get_grow_effectors(grow[0])

    return render_template('index.html',    user_grows=grows,
                                            sensors=grow_sensors,
                                            effectors=grow_effectors, 
                                            plants=grow_plants, 
                                            sensor_types=database.get_sensor_types(),
                                            effector_types=database.get_effector_types(),
                                            photoperiods=database.get_photoperiods(),
                                            genders=database.get_genders(),
                                            intensities=database.get_intensities())

@app.route('/login', methods=['GET', 'POST'])
def login():
    is_login_valid = True

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        if database.verify_password(email, password):
            user_id = database.get_user_id(email)

            session['logged_in'] = True
            session['user_id'] = user_id
            session['is_admin'] = database.get_admin(user_id)

            return redirect(url_for('index'))
        else:
            is_login_valid = False
    
    return render_template('auth/login.html', is_login_valid=is_login_valid)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/register", methods=['GET','POST'])
def register():
    print('register')
    if 'email' in request.form and 'password' in request.form and 'c_password' in request.form:
        email = request.form['email']
        password = request.form['password']
        password_confirmation = request.form['c_password']
        
        if password != password_confirmation:
            print("As senhas não coincidem")
            return render_template('auth/register.html')
        
        if not is_valid_email(email):
            print("Email inválido")
            return render_template('auth/register.html')
            
        if not is_strong_password(password):
            print("A senha deve ter pelo menos 8 caracteres, incluindo maiúsculas, minúsculas e números")
            return render_template('auth/register.html')
        
        if database.create_user(email, password):
            print("Usuário criado com sucesso! Faça login.")
            return redirect(url_for('login'))
        else:
            print("Erro ao criar usuário. Email já existe.")
    
    return render_template('auth/register.html')

##################################################################################################
@app.route('/user', methods=['GET', 'POST'])
def user():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    return render_template(
        'user/index.html', 
        get_admin=database.get_admin, 
        users=database.get_users(), 
        current_user_id=session['user_id'],
        current_user_email=database.get_user_email(session['user_id']),
        is_admin=session['is_admin']
    )

@app.route('/user/create', methods=['GET', 'POST'])
def create_user():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        new_password = request.form['password']
        is_admin = request.form.get('is_admin', "0")

        if not is_valid_email(email):
            flash("Email inválido")
            return redirect(url_for('user'))
            
        if not is_strong_password(new_password):
            flash("A senha deve ter pelo menos 8 caracteres, incluindo maiúsculas, minúsculas e números")
            return redirect(url_for('user'))

        if database.create_user(email, new_password, bool(int(is_admin))):
            flash("Usuário criado com sucesso")
        else:
            flash("Erro ao criar usuário. Email já existe.")
    
    return redirect(url_for('user'))

@app.route('/user/update/<id>', methods=['GET', 'POST'])
def update_user(id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST' and 'email' in request.form and 'new_password' in request.form and 'is_admin' in request.form:
        email = request.form['email']
        new_password = request.form['new_password']
        is_admin = request.form['is_admin']

        if not is_valid_email(email):
            flash("Email inválido")
            return redirect(url_for('user'))
            
        if new_password and not is_strong_password(new_password):
            flash("A senha deve ter pelo menos 8 caracteres, incluindo maiúsculas, minúsculas e números")
            return redirect(url_for('user'))

        database.update_user(id, email, new_password, is_admin)
        flash("Usuário atualizado com sucesso")
    
    return redirect(url_for('user'))

@app.route('/user/delete/<id>', methods=['GET', 'POST'])
def delete_user(id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    database.delete_user(id)
    flash("Usuário deletado com sucesso")
    return redirect(url_for('user'))

##################################################################################################
@app.route('/plant/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def plant_index(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    plant = database.get_plant(plant_id)
    if len(plant) == 0:
        plant = [ None ]
    else:
        plant = plant[0]

    return render_template(
        'plant/index.html',
        grow_id=grow_id,
        plant=plant,
        waterings=database.get_plant_waterings(plant_id),
        damages=database.get_plant_damages(plant_id),
        trainings=database.get_plant_trainings(plant_id),
        transplantings=database.get_plant_transplantings(plant_id),
        feedings=database.get_plant_feedings(plant_id),
        photoperiods=database.get_photoperiods(),
        genders=database.get_genders(),
        intensities=database.get_intensities()
    )

@app.route('/plant/create/<grow_id>', methods=['GET', 'POST'])
def create_plant(grow_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'date' in request.form and 'photoperiod_id' in request.form and 'gender_id' in request.form:
        database.insert_plant(grow_id, request.form['name'], request.form['date'], request.form['photoperiod_id'], request.form['gender_id'])
    return redirect(url_for('index'))

@app.route('/plant/update/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def update_plant(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'date' in request.form and 'photoperiod_id' in request.form and 'gender_id' in request.form:
        database.update_plant(plant_id, request.form['name'], request.form['date'], request.form['photoperiod_id'], request.form['gender_id'])
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

@app.route('/plant/delete/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def delete_plant(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    database.delete_plant(plant_id)
    return redirect(url_for('index'))

################################################################################################## 
@app.route('/watering/create/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def create_watering(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'date' in request.form and 'mililiter' in request.form:
        database.insert_watering(plant_id, request.form['date'], request.form['mililiter'])
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

@app.route('/watering/delete/<grow_id>/<plant_id>/<watering_id>', methods=['GET', 'POST'])
def delete_watering(grow_id, plant_id, watering_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    database.delete_watering(watering_id)
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

################################################################################################## 
@app.route('/training/create/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def create_training(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # TODO: create training
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

@app.route('/training/delete/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def delete_training(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # TODO: delete training
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

################################################################################################## 
@app.route('/feeding/create/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def create_feeding(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # TODO: create feeding
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

@app.route('/feeding/delete/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def delete_feeding(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # TODO: delete feeding
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

################################################################################################## 
@app.route('/transplanting/create/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def create_transplanting(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # TODO: create transplanting
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

@app.route('/transplanting/delete/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def delete_transplanting(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # TODO: delete transplanting
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

################################################################################################## 
@app.route('/damage/create/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def create_damage(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # TODO: create damage
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

@app.route('/damage/delete/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def delete_damage(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # TODO: delete damage
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

################################################################################################## 
@app.route('/grow/create', methods=['GET', 'POST'])
def create_grow():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'lenght' in request.form and 'width' in request.form and 'height' in request.form:
        database.insert_grow(session['user_id'], request.form['name'], request.form['lenght'], request.form['width'], request.form['height'])
        
    return redirect(url_for('index'))

@app.route('/grow/update/<grow_id>', methods=['GET', 'POST'])
def update_grow(grow_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'lenght' in request.form and 'width' in request.form and 'height' in request.form:
        database.update_grow(grow_id, request.form['name'], request.form['lenght'], request.form['width'], request.form['height'])
    return redirect(url_for('index'))

@app.route('/grow/delete/<grow_id>', methods=['GET', 'POST'])
def delete_grow(grow_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    database.delete_grow(grow_id)
    return redirect(url_for('index'))

################################################################################################## 
@app.route('/sensor/create/<grow_id>', methods=['GET', 'POST'])
def create_sensor(grow_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'sensor_type_id' in request.form:
        database.insert_sensor(grow_id, request.form['name'], request.form['sensor_type_id'])
    return redirect(url_for('index'))

@app.route('/sensor/delete/<grow_id>/<sensor_id>', methods=['GET', 'POST'])
def delete_sensor(grow_id, sensor_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    database.delete_sensor(sensor_id)
    return redirect(url_for('index'))

@app.route('/sensor/update/<grow_id>/<sensor_id>', methods=['GET', 'POST'])
def update_sensor(grow_id, sensor_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'sensor_type_id' in request.form and 'ip' in request.form:
        database.update_sensor(sensor_id, request.form['name'], request.form['sensor_type_id'], request.form['ip'])
    return redirect(url_for('index'))

@app.route('/sensor/data/<sensor_id>/<value>', methods=['GET', 'POST'])
def sensor_data(sensor_id, value):
    database.insert_sensor_data(sensor_id, value)
    return '1'

################################################################################################## 
@app.route('/effector/create/<grow_id>', methods=['GET', 'POST'])
def create_effector(grow_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'effector_type_id' in request.form:
        database.insert_effector(grow_id, request.form['effector_type_id'], request.form['name'])
    return redirect(url_for('index'))

@app.route('/effector/delete/<grow_id>/<effector_id>', methods=['GET', 'POST'])
def delete_effector(grow_id, effector_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    database.delete_effector(effector_id)
    return redirect(url_for('index'))

@app.route('/effector/update/<grow_id>/<effector_id>', methods=['GET', 'POST'])
def update_effector(grow_id, effector_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'effector_type_id' in request.form and 'ip' in request.form:
        bounded = False
        scheduled = False
        bounded_sensor_id = 0
        threshold = 0
        on_time = ''
        off_time = ''
        normal_on = False

        if 'normal_on' in request.form:
            normal_on = True

        if 'bounded' in request.form and 'bounded_sensor_id' in request.form and 'threshold' in request.form:
            bounded = True
            bounded_sensor_id = request.form['bounded_sensor_id']
            threshold = request.form['threshold']
        
        if 'scheduled' in request.form and 'on_time' in request.form and 'off_time' in request.form:
            scheduled = True
            on_time = request.form['on_time']
            off_time = request.form['off_time']
        
        database.update_effector(effector_id, request.form['name'], request.form['effector_type_id'], request.form['ip'], normal_on, scheduled ,on_time, off_time, bounded, bounded_sensor_id, threshold)
    
    return redirect(url_for('index'))

@app.route('/effector/data/<effector_id>', methods=['GET', 'POST'])
def effector_data(effector_id):
    effector_data = database.get_effector(effector_id)
    
    if not effector_data or len(effector_data) == 0:
        return "0"
    
    effector = effector_data[0]
    id, grow_id, effector_type_id, name, ip, normal_on, power_on, scheduled, on_time, off_time, bounded, bounded_sensor_id, threshold = effector
    
    is_scheduled = bool(scheduled) == True
    is_bounded = bool(bounded) == True
    is_normal_on = bool(normal_on) == True
    current_power_on = bool(power_on)

    if is_scheduled:
        if isinstance(on_time, datetime.timedelta):
            on_time = (datetime.datetime.min + on_time).time()
        if isinstance(off_time, datetime.timedelta):
            off_time = (datetime.datetime.min + off_time).time()

        now = datetime.datetime.now().time()

        pass_on_time = now >= on_time
        before_off_time = now <= off_time
        current_power_on = pass_on_time and before_off_time

        if is_normal_on:
            current_power_on = not current_power_on

    elif is_bounded:
        sensor_value = database.get_last_sensor_data_value(bounded_sensor_id)
        if sensor_value and len(sensor_value) > 0:
            current_power_on = sensor_value[0][0] >= threshold
            if is_normal_on:
                current_power_on = not current_power_on
        else:
            current_power_on = False
        
    database.set_effector_power_on(effector_id, current_power_on)

    return str(int(current_power_on))

if __name__ == '__main__':
    app.run(host='192.168.1.7', debug=True)