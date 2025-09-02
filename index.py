from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort, jsonify
from flask import Flask
import logging
import database
import datetime
import os

import re

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

db = database.Database(db_host, db_name, db_user, db_password)

@app.errorhandler(Exception)
def handle_exception(e):
    return f"Ocorreu um erro interno: {e}", 500

@app.route("/")
def index():
    if 'logged_in' not in session or session['logged_in'] != True:
        return redirect(url_for('login'))
    
    grows = db.get_user_grows(session['user_id'])

    grow_plants = {}
    for grow in grows:
        grow_plants[grow[0]] = db.get_grow_plants(grow[0])

    grow_sensors = {}
    for grow in grows:
        grow_sensors[grow[0]] = db.get_grow_sensors(grow[0])

    grow_effectors = {}
    for grow in grows:
        grow_effectors[grow[0]] = db.get_grow_effectors(grow[0])

    last_sensor_data = {}
    sensor_data = {}  # Mudar a estrutura para ser por grow_id -> sensor_id
    for grow in grows:
        last_sensor_data[grow[0]] = {}
        sensor_data[grow[0]] = {}  # Inicializar como dicionário por grow
        for sensor in grow_sensors[grow[0]]:
            sensor_id = sensor[0]
            result = db.get_last_sensor_data_value_and_date(sensor_id)
            
            # Verifica se tem resultado e se tem pelo menos 2 valores
            if result and len(result) > 0 and len(result[0]) >= 2:
                value, timestamp = result[0]
            else:
                value, timestamp = 0, None
            
            if timestamp and isinstance(timestamp, datetime.timedelta):
                timestamp = (datetime.datetime.min + timestamp).time()

            last_sensor_data[grow[0]][sensor_id] = [value, timestamp]
            
            # Buscar dados históricos do sensor - formato correto para gráficos
            historical_data = db.get_sensor_data(sensor_id)
            sensor_data[grow[0]][sensor_id] = historical_data

    return render_template('index.html', 
                         user_grows=grows,
                         sensors=grow_sensors,
                         effectors=grow_effectors, 
                         plants=grow_plants, 
                         last_sensor_data=last_sensor_data,
                         sensor_data=sensor_data,
                         sensor_types=db.get_sensor_types(),
                         effector_types=db.get_effector_types(),
                         photoperiods=db.get_photoperiods(),
                         genders=db.get_genders(),
                         intensities=db.get_intensities())

@app.route('/login', methods=['GET', 'POST'])
def login():
    is_login_valid = True

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        if db.verify_password(email, password):
            user_id = db.get_user_id(email)

            session['logged_in'] = True
            session['user_id'] = user_id
            session['is_admin'] = db.get_admin(user_id)

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
        
        if db.create_user(email, password):
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
        get_admin=db.get_admin, 
        users=db.get_users(), 
        current_user_id=session['user_id'],
        current_user_email=db.get_user_email(session['user_id']),
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

        if db.create_user(email, new_password, bool(int(is_admin))):
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

        db.update_user(id, email, new_password, is_admin)
        flash("Usuário atualizado com sucesso")
    
    return redirect(url_for('user'))

@app.route('/user/delete/<id>', methods=['GET', 'POST'])
def delete_user(id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    db.delete_user(id)
    flash("Usuário deletado com sucesso")
    return redirect(url_for('user'))

##################################################################################################
@app.route('/plant/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def plant_index(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    plant = db.get_plant(plant_id)
    if not plant or len(plant) == 0:
        plant = [ None ]
    else:
        plant = plant[0]

    return render_template(
        'plant/index.html',
        grow_id=grow_id,
        plant=plant,
        waterings=db.get_plant_waterings(plant_id),
        damages=db.get_plant_damages(plant_id),
        trainings=db.get_plant_trainings(plant_id),
        transplantings=db.get_plant_transplantings(plant_id),
        feedings=db.get_plant_feedings(plant_id),
        photoperiods=db.get_photoperiods(),
        genders=db.get_genders(),
        intensities=db.get_intensities()
    )

@app.route('/plant/create/<grow_id>', methods=['GET', 'POST'])
def create_plant(grow_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'date' in request.form and 'photoperiod_id' in request.form and 'gender_id' in request.form:
        db.insert_plant(grow_id, request.form['name'], request.form['date'], request.form['photoperiod_id'], request.form['gender_id'])
    return redirect(url_for('index'))

@app.route('/plant/update/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def update_plant(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'date' in request.form and 'photoperiod_id' in request.form and 'gender_id' in request.form:
        db.update_plant(plant_id, request.form['name'], request.form['date'], request.form['photoperiod_id'], request.form['gender_id'])
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

@app.route('/plant/delete/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def delete_plant(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    db.delete_plant(plant_id)
    return redirect(url_for('index'))

################################################################################################## 
@app.route('/watering/create/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def create_watering(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'date' in request.form and 'mililiter' in request.form:
        db.insert_watering(plant_id, request.form['date'], request.form['mililiter'])
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

@app.route('/watering/delete/<grow_id>/<plant_id>/<watering_id>', methods=['GET', 'POST'])
def delete_watering(grow_id, plant_id, watering_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    db.delete_watering(watering_id)
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

################################################################################################## 
@app.route('/training/create/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def create_training(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'date' in request.form and 'training_type_id' in request.form:
        db.insert_training(plant_id, request.form['training_type_id'], request.form['date'])
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

@app.route('/training/delete/<grow_id>/<plant_id>/<training_id>', methods=['GET', 'POST'])
def delete_training(grow_id, plant_id, training_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # Implementar delete_training no database.py se necessário
    db.execute_query("DELETE FROM training WHERE id = %s", (training_id,))
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

################################################################################################## 
@app.route('/feeding/create/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def create_feeding(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if all(key in request.form for key in ['date', 'dosage', 'concentration', 'nitrogen', 'phosphorus', 'potassium']):
        db.insert_feeding(
            plant_id, 
            request.form['date'], 
            request.form['dosage'], 
            request.form['concentration'], 
            request.form['nitrogen'], 
            request.form['phosphorus'], 
            request.form['potassium']
        )
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

@app.route('/feeding/delete/<grow_id>/<plant_id>/<feeding_id>', methods=['GET', 'POST'])
def delete_feeding(grow_id, plant_id, feeding_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    db.execute_query("DELETE FROM feeding WHERE id = %s", (feeding_id,))
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

################################################################################################## 
@app.route('/transplanting/create/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def create_transplanting(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'date' in request.form:
        db.execute_query(
            "INSERT INTO transplanting (plant_id, date, lenght, width, height, radius) VALUES (%s, DATE(%s), %s, %s, %s, %s)",
            (plant_id, request.form['date'], 
             request.form.get('lenght', 0), 
             request.form.get('width', 0), 
             request.form.get('height', 0), 
             request.form.get('radius', 0))
        )
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

@app.route('/transplanting/delete/<grow_id>/<plant_id>/<transplanting_id>', methods=['GET', 'POST'])
def delete_transplanting(grow_id, plant_id, transplanting_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    db.execute_query("DELETE FROM transplanting WHERE id = %s", (transplanting_id,))
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

################################################################################################## 
@app.route('/damage/create/<grow_id>/<plant_id>', methods=['GET', 'POST'])
def create_damage(grow_id, plant_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if all(key in request.form for key in ['date', 'damage_type_id', 'intensity_id']):
        db.execute_query(
            "INSERT INTO damage (plant_id, date, damage_type_id, intensity_id) VALUES (%s, DATE(%s), %s, %s)",
            (plant_id, request.form['date'], request.form['damage_type_id'], request.form['intensity_id'])
        )
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

@app.route('/damage/delete/<grow_id>/<plant_id>/<damage_id>', methods=['GET', 'POST'])
def delete_damage(grow_id, plant_id, damage_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    db.execute_query("DELETE FROM damage WHERE id = %s", (damage_id,))
    return redirect(url_for('plant_index', grow_id=grow_id, plant_id=plant_id))

################################################################################################## 
@app.route('/grow/create', methods=['GET', 'POST'])
def create_grow():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'lenght' in request.form and 'width' in request.form and 'height' in request.form:
        db.insert_grow(session['user_id'], request.form['name'], request.form['lenght'], request.form['width'], request.form['height'])
        
    return redirect(url_for('index'))

@app.route('/grow/update/<grow_id>', methods=['GET', 'POST'])
def update_grow(grow_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'lenght' in request.form and 'width' in request.form and 'height' in request.form:
        db.update_grow(grow_id, request.form['name'], request.form['lenght'], request.form['width'], request.form['height'])
    return redirect(url_for('index'))

@app.route('/grow/delete/<grow_id>', methods=['GET', 'POST'])
def delete_grow(grow_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    db.execute_query("DELETE FROM grow WHERE id = %s", (grow_id,))
    return redirect(url_for('index'))

################################################################################################## 
@app.route('/sensor/create/<grow_id>', methods=['GET', 'POST'])
def create_sensor(grow_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'sensor_type_id' in request.form:
        db.insert_sensor(grow_id, request.form['name'], request.form['sensor_type_id'])
    return redirect(url_for('index'))

@app.route('/sensor/delete/<grow_id>/<sensor_id>', methods=['GET', 'POST'])
def delete_sensor(grow_id, sensor_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    db.delete_sensor(sensor_id)
    return redirect(url_for('index'))

@app.route('/sensor/update/<grow_id>/<sensor_id>', methods=['GET', 'POST'])
def update_sensor(grow_id, sensor_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'sensor_type_id' in request.form and 'ip' in request.form and 'data_retention_days' in request.form:
        db.update_sensor(sensor_id, request.form['name'], request.form['sensor_type_id'], request.form['ip'], request.form['data_retention_days'])
    return redirect(url_for('index'))

@app.route('/sensor/data/<sensor_id>/<value>', methods=['GET', 'POST'])
def sensor_data(sensor_id, value):
    try:
        result = db.insert_sensor_data(sensor_id, value)
        # Se o método retornar algo, ignore ou use conforme necessário
        return '1'
    except Exception as e:
        print(f"Erro ao inserir dados do sensor: {e}")
        return '0'
    
################################################################################################## 
@app.route('/effector/create/<grow_id>', methods=['GET', 'POST'])
def create_effector(grow_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if 'name' in request.form and 'effector_type_id' in request.form:
        db.insert_effector(grow_id, request.form['effector_type_id'], request.form['name'])
    return redirect(url_for('index'))

@app.route('/effector/delete/<grow_id>/<effector_id>', methods=['GET', 'POST'])
def delete_effector(grow_id, effector_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    db.delete_effector(effector_id)
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
        
        db.update_effector(effector_id, request.form['name'], request.form['effector_type_id'], request.form['ip'], normal_on, scheduled ,on_time, off_time, bounded, bounded_sensor_id, threshold)
    
    return redirect(url_for('index'))

@app.route('/effector/data/<effector_id>', methods=['GET', 'POST'])
def effector_data(effector_id):
    effector_data = db.get_effector(effector_id)
    
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
        sensor_value = db.get_last_sensor_data_value(bounded_sensor_id)
        if sensor_value and len(sensor_value) > 0:
            current_power_on = sensor_value[0][0] >= threshold
            if is_normal_on:
                current_power_on = not current_power_on
        else:
            current_power_on = False
        
    db.set_effector_power_on(effector_id, current_power_on)

    db.update_effector_request_time(effector_id)

    return str(int(current_power_on))

# No index.py, adicione esta rota
@app.route('/api/sensor/data/<sensor_id>')
def api_sensor_data(sensor_id):
    try:
        session = db._get_session()
        # Buscar dados dos últimos 7 dias por padrão
        sensor_data = session.execute(
            text("SELECT datetime, value FROM sensor_data WHERE sensor_id = :sensor_id AND datetime > NOW() - INTERVAL 7 DAY ORDER BY datetime"),
            {'sensor_id': sensor_id}
        ).fetchall()
        
        # Converter para formato JSON
        data = []
        for row in sensor_data:
            data.append([
                row[0].strftime('%Y-%m-%d %H:%M:%S'),  # timestamp como string
                float(row[1])  # valor como float
            ])
        
        return jsonify(data)
    except Exception as e:
        print(f"Erro ao buscar dados do sensor: {e}")
        return jsonify([])
    finally:
        session.close()
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(host='192.168.1.7', debug=True)