from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort, jsonify
from flask import Flask
from scripts.database import Database
import logging
import datetime
import os

app = Flask(__name__)
app.secret_key = '1234'
site = Blueprint('site', __name__, template_folder='templates')
basedir = os.path.abspath(os.path.dirname(__file__))
# Configurar logging
logging.basicConfig(
    filename='app.log',  # pasta com permissão de escrita
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)
database = Database("localhost", "growcontrol", "root", "root")
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

    power_on = is_normal_on

    if is_scheduled:
        if isinstance(on_time, datetime.timedelta):
            on_time = (datetime.datetime.min + on_time).time()
        if isinstance(off_time, datetime.timedelta):
            off_time = (datetime.datetime.min + off_time).time()

        now = datetime.datetime.now().time()

        pass_on_time = now >= on_time
        before_off_time = now <= off_time
        power_on = pass_on_time and before_off_time

        if is_normal_on:
            power_on = not power_on

    elif is_bounded:
        print(database.get_last_sensor_data_value(bounded_sensor_id))
        
        power_on = database.get_last_sensor_data_value(bounded_sensor_id)[0][0] >= threshold
        if is_normal_on:
            power_on = not power_on
        
    database.set_effector_power_on(effector_id, power_on)

    return str(int(power_on))

if __name__ == '__main__':
    app.run()