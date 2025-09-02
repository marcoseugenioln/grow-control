from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort, jsonify
from flask import Flask
import logging
import mysql.connector
import datetime
import os

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
            autocommit=True
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
            "INSERT IGNORE INTO effector_type (name, description) VALUES ('Fan',''),('Lights',''),('Water Supplier',''),('Exhauster',''),('Blower',''),('Humidifier',''),('Dehumidifier','');",
            "INSERT IGNORE INTO user (email, password, is_admin) VALUES ('root@root.com','root',1),('user@user.com','user',0);"
        ]
        for stmt in inserts_sql:
            self.query.execute(stmt)

    def connect(self):
        """Estabelece nova conexão"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
                port=3306,
                buffered=True,
                ssl_disabled=True,
                autocommit=True
            )
            
            self.query = self.connection.cursor(buffered=True)
            print("Conexão MySQL estabelecida")
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            raise

    def ensure_connection(self):
        """Verifica e reconecta se necessário"""
        try:
            self.connection.ping(reconnect=True, attempts=3, delay=5)
        except:
            print("Reconectando ao MySQL...")
            self.connect()


    def execute_query(self, query, params=None):
        print(f'{datetime.datetime.now()} - {query}')
        self.ensure_connection()
        
        try:
            self.query.execute(query, params or ())
            
            # Verifica se a query retorna resultados
            if self.query.description:  # Se há descrição de colunas, é SELECT
                retrieved_values = self.query.fetchall()
                print(f'{datetime.datetime.now()} - {retrieved_values}')
                return retrieved_values
            else:
                # Para queries que não retornam dados
                affected_rows = self.query.rowcount
                print(f'{datetime.datetime.now()} - Linhas afetadas: {affected_rows}')
                return affected_rows  # Retorna número de linhas afetadas
                
        except Exception as e:
            print(f'{datetime.datetime.now()} - Erro: {e}')
            self.connection.rollback()
            raise
        
    def user_exists(self, email: str, password: str) -> bool:
        account = self.execute_query(f"SELECT * FROM user WHERE email='{email}' AND password='{password}'")
        if not account:
            return False
        return True
    
    def get_user_id(self, email: str, password: str):
        user_id = self.execute_query(f"SELECT id FROM user WHERE email='{email}' AND password='{password}';")
        if len(user_id) > 0:   
            return user_id[0][0]
        else:
            return str(0)
        
    def get_admin(self, user_id):
        is_admin = self.execute_query(f"SELECT is_admin FROM user WHERE id={user_id};")
        if len(is_admin) > 0:
            if int(is_admin[0][0]) == 0:
                return False
        return True
    
    def insert_user(self, email: str, password: str, is_admin: str):
        self.execute_query(f"INSERT OR IGNORE INTO user(email, password, is_admin) values ('{email}', '{password}', {is_admin});")
    
    def get_user_email(self, user_id: int) -> str:
        email = self.execute_query(f"SELECT email FROM user WHERE id={user_id}")
        if email:
            return email[0]
        else:
            return ""
        
    def get_user_password(self, user_id: int) -> str:
        password = self.execute_query(f"SELECT password FROM user WHERE id={user_id}")
        if password:
            return password[0]
        else:
            return ""
        
    def get_users(self):
        return self.execute_query(f"SELECT id, email, password FROM user")
    def alter_password(self, user_id, password):
        self.execute_query(f"UPDATE user SET password = '{password}' WHERE id={user_id}")
    def alter_email(self, user_id, email):
        self.execute_query(f"UPDATE user SET email = '{email}' WHERE id={user_id}")
    def delete_user(self, id):
        self.execute_query(f"DELETE FROM user WHERE id={id};")
    def update_user(self, user_id, email, password, is_admin):
        self.execute_query(f"UPDATE user SET email = '{email}', password = '{password}', is_admin = {is_admin} WHERE id={user_id};")
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
        self.execute_query(f"INSERT INTO grow(user_id, name, lenght, width, height) values ({user_id}, '{name}', {lenght}, {width}, {height});")
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
        query = f"""
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
                WHERE grow_id = {grow_id};
                """
        return self.execute_query(query)
    
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
    def insert_sensor(self, grow_id, name, sensor_type_id):
        self.execute_query(f"insert into sensor (grow_id, name, sensor_type_id) values ({grow_id}, '{name}', {sensor_type_id});")
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
            bounded_sensor_id = {bounded_sensor_id if int(bounded_sensor_id) > 0 else 'NULL'},
            threshold = {threshold},
            on_time = {f"TIME('{on_time}')" if on_time else 'NULL'},
            off_time = {f"TIME('{off_time}')" if off_time else 'NULL'}
        WHERE id = {effector_id};
        """
        self.execute_query(sql)

app = Flask(__name__)
app.secret_key = '1234'
site = Blueprint('site', __name__, template_folder='templates')
basedir = os.path.abspath(os.path.dirname(__file__))
database = Database("localhost", "growcontrol", "root", "root")

@app.errorhandler(Exception)
def handle_exception(e):
    return f"Ocorreu um erro interno: {e}", 500
@app.route("/")
def index():
    if 'logged_in' in session:
        if session['logged_in'] != True:
            return redirect(url_for('login'))
    else:
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

        if database.user_exists(email, password):

            user_id = database.get_user_id(email, password)

            session['logged_in'] = True
            session['user_id'] = user_id
            session['is_admin'] = database.get_admin(user_id)

            return redirect(url_for(f'index'))
        else:
            is_login_valid = False
    
    return render_template('auth/login.html', is_login_valid = is_login_valid)
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'logged_in' in session:
        session.pop('logged_in')

    if 'user_id' in session:    
        session.pop('user_id')
    
    if 'is_admin' in session:
        session.pop('is_admin')

    return redirect(url_for(f'login'))
@app.route("/register", methods=['GET','POST'])
def register():

    is_logged = False

    if (request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'password_c' in request.form):
        
        email = request.form['email']
        password = request.form['password']
        password_c = request.form['password_c']

        if database.insert_user(email, password, password_c):
            return redirect(url_for('login'))   

        if 'logged_in' in session:
            if session['logged_in'] == True:
                is_logged = True                 
    
    return render_template('auth/register.html', logged_in = is_logged)
##################################################################################################
@app.route('/user', methods=['GET', 'POST'])
def user():
    
    return render_template(
        'user/index.html', 
        get_admin=database.get_admin, 
        users = database.get_users(), 
        current_user_id = session['user_id'],
        current_user_email = database.get_user_email(session['user_id']),
        current_user_password = database.get_user_password(session['user_id']),
        is_admin = session['is_admin']
        )
@app.route('/user/create', methods=['GET', 'POST'])
def create_user():
    
    if (request.method == 'POST' and 'email' in request.form and 'new_password' in request.form ):
        
        email = request.form['email']
        new_password = request.form['new_password']

        if('is_admin' in request.form):
            is_admin = request.form['is_admin']
        else:
            is_admin = "0"

        if database.insert_user(email, new_password, is_admin):
            if 'user_id' in session:
                return redirect(url_for('user'))

        return redirect('/login')
    
    return redirect('/login')
@app.route('/user/update/<id>', methods=['GET', 'POST'])
def update_user(id):
    if (request.method == 'POST' and 'email' in request.form and 'new_password' in request.form and 'is_admin' in request.form):
        
        email = request.form['email']
        new_password = request.form['new_password']
        is_admin = request.form['is_admin']

        database.update_user(id, email, new_password, is_admin)
        return redirect(url_for('user'))  
        
    return redirect(url_for('user'))
@app.route('/user/delete/<id>', methods=['GET', 'POST'])
def delete_user(id):
    database.delete_user(id)
    return redirect(url_for('user'))
##################################################################################################
@app.route('/plant/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def plant_index(grow_id, plant_id):

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
    if 'name' in request.form and 'date' in request.form and 'photoperiod_id' in request.form and 'gender_id' in request.form:
        database.insert_plant(grow_id, request.form['name'], request.form['date'], request.form['photoperiod_id'], request.form['gender_id'])
    return redirect(url_for('index'))
@app.route('/plant/update/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def update_plant(grow_id, plant_id):
    if 'name' in request.form and 'date' in request.form and 'photoperiod_id' in request.form and 'gender_id' in request.form:
        database.update_plant(plant_id, request.form['name'], request.form['date'], request.form['photoperiod_id'], request.form['gender_id'])
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))
@app.route('/plant/delete/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def delete_plant(grow_id, plant_id):
    database.delete_plant(plant_id)
    return redirect(url_for('index'))
################################################################################################## 
@app.route('/watering/create/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def create_watering(grow_id, plant_id):
    if 'date' in request.form and 'mililiter' in request.form:
        database.insert_watering(plant_id, request.form['date'], request.form['mililiter'])
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))
@app.route('/watering/delete/<grow_id>/<plant_id>/<watering_id>', methods=['GET', 'POST'])
def delete_watering(grow_id, plant_id, watering_id):
    database.delete_watering(watering_id)
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))
################################################################################################## 
@app.route('/training/create/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def create_training(grow_id, plant_id):
    # TODO: create training
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))
@app.route('/training/delete/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def delete_training(grow_id, plant_id):
    # TODO: delete training
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))
################################################################################################## 
@app.route('/feeding/create/<plant_id>', methods=['GET', 'POST'])
def create_feeding(grow_id, plant_id):
    # TODO: create feeding
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))
@app.route('/feeding/delete/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def delete_feeding(grow_id, plant_id):
    # TODO: delete feeding
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))
################################################################################################## 
@app.route('/transplanting/create/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def create_transplanting(grow_id, plant_id):
    # TODO: create transplanting
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))
@app.route('/transplanting/delete/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def delete_transplanting(grow_id, plant_id):
    # TODO: delete transplanting
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))
################################################################################################## 
@app.route('/damage/create/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def create_damage(grow_id, plant_id):
    # TODO: create damage
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))
@app.route('/damage/delete/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def delete_damage(grow_id, plant_id):
    # TODO: delete damage
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))
################################################################################################## 
@app.route('/grow/create', methods=['GET', 'POST'])
def create_grow():
    if 'name' in request.form and 'lenght' in request.form and 'width' in request.form and 'height' in request.form:
        database.insert_grow(session['user_id'], request.form['name'],  request.form['lenght'], request.form['width'], request.form['height'])
        
    return redirect(url_for('index'))
@app.route('/grow/update/<grow_id>', methods=['GET', 'POST'])
def update_grow(grow_id):
    if 'name' in request.form and 'lenght' in request.form and 'width' in request.form and 'height' in request.form:
        database.update_grow(grow_id, request.form['name'],  request.form['lenght'], request.form['width'], request.form['height'])
    return redirect(url_for('index'))
@app.route('/grow/delete/<grow_id>', methods=['GET', 'POST'])
def delete_grow(grow_id):
    database.delete_grow(grow_id)
    return redirect(url_for('index'))
################################################################################################## 
@app.route('/sensor/create/<grow_id>', methods=['GET', 'POST'])
def create_sensor(grow_id):
    if 'name' in request.form and 'sensor_type_id' in request.form:
        database.insert_sensor(grow_id, request.form['name'], request.form['sensor_type_id'])
    return redirect(url_for('index'))
@app.route('/sensor/delete/<grow_id>/<sensor_id>', methods=['GET', 'POST'])
def delete_sensor(grow_id, sensor_id):
    database.delete_sensor(sensor_id)
    return redirect(url_for('index'))
@app.route('/sensor/update/<grow_id>/<sensor_id>', methods=['GET', 'POST'])
def update_sensor(grow_id, sensor_id):
    if 'name' in request.form and 'sensor_type_id' in request.form and 'ip' in request.form:
        database.update_sensor(sensor_id, request.form['name'], request.form['sensor_type_id'], request.form['ip'])
    return redirect(url_for('index'))
@app.route('/sensor/data/<sensor_id>/<value>', methods=['GET', 'POST'])
def sensor_data(sensor_id, value):
    # insert sensor data into database
    database.insert_sensor_data(sensor_id, value)
    return '1'
################################################################################################## 
@app.route('/effector/create/<grow_id>', methods=['GET', 'POST'])
def create_effector(grow_id):
    if 'name' in request.form and 'effector_type_id' in request.form:
        database.insert_effector(grow_id, request.form['effector_type_id'], request.form['name'])
    return redirect(url_for('index'))
@app.route('/effector/delete/<grow_id>/<effector_id>', methods=['GET', 'POST'])
def delete_effector(grow_id, effector_id):
    database.delete_effector(effector_id)
    return redirect(url_for('index'))
@app.route('/effector/update/<grow_id>/<effector_id>', methods=['GET', 'POST'])
def update_effector(grow_id, effector_id):

    print(request.form)

    if 'name' in request.form and 'effector_type_id' in request.form and 'ip' in request.form:

        bounded = False
        scheduled = False
        bounded_sensor_id = 0
        threshold = 0
        on_time = ''
        off_time = ''
        normal_on = False

        if 'normal_on' in request.form:
            print(request.form['normal_on'])
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
def device_power_on(effector_id):

    id, grow_id, effector_type_id, name, ip, normal_on, power_on, scheduled, on_time, off_time, bounded, bounded_sensor_id, threshold = database.get_effector(effector_id)[0]
    
    # get device configuration
    is_scheduled = bool(scheduled) == True
    is_bounded = bool(bounded) == True
    is_normal_on = bool(normal_on) == True

    turn_on = power_on

    if is_scheduled:
        if isinstance(on_time, datetime.timedelta):
            on_time = (datetime.datetime.min + on_time).time()
        if isinstance(off_time, datetime.timedelta):
            off_time = (datetime.datetime.min + off_time).time()

        now = datetime.datetime.now().time()

        pass_on_time = now >= on_time
        before_off_time = now <= off_time
        turn_on = pass_on_time and before_off_time

        if is_normal_on:
            turn_on = not power_on

    elif is_bounded:
        print(database.get_last_sensor_data_value(bounded_sensor_id))
        
        turn_on = database.get_last_sensor_data_value(bounded_sensor_id)[0][0] >= threshold
        if is_normal_on:
            turn_on = not power_on
        
    database.set_effector_power_on(effector_id, turn_on)

    return str(int(turn_on))

if __name__ == '__main__':
    app.run()
else:
    application = app