from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort, jsonify
from flask import Flask
from scripts.grow import Grow
from scripts.database import Database
import json
import sys
import logging

app = Flask(__name__)
app.secret_key = '1234'

site = Blueprint('site', __name__, template_folder='templates')

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

with open(str(sys.argv[1])) as config_file:
    app_config = json.load(config_file)

database = Database(database_path='database/schema.db', schema_file='database/schema.sql')

grow = Grow(auto_mode=app_config['auto_mode'],
            min_humidity=app_config['min_humidity'],
            max_humidity=app_config['max_humidity'],
            lights_on_time=app_config['lights_on_time'],
            lights_off_time=app_config['lights_off_time'])

##################################################################################################
@app.route("/")
def index():
    return render_template('index.html',
                            temperature=grow.temperature,
                            humidity=grow.humidity,
                            auto_mode=grow.auto_mode,
                            humidifier_on=grow.humidifier_on,
                            min_humidity=grow.min_humidity,
                            max_humidity=grow.max_humidity,
                            lights_on=grow.lights_on,
                            lights_on_time=grow.lights_on_time,
                            lights_off_time=grow.lights_off_time)

@app.route("/m_grow_settings_cmd", methods=['GET','POST'])
def grow_settings_cmd():
    
    if request.method == 'POST':

        auto_mode = False
        lights_on_time = None
        lights_off_time = None
        humidifier_on = False
        min_humidity = 0
        max_humidity = 0
        lights_on = False
        air_circulation_capacity = 0

        if 'auto_mode' in request.form:
            auto_mode = request.form['auto_mode'] == 'on'

        if 'humidifier_on' in request.form:
            humidifier_on = request.form['humidifier_on'] == 'on'

        if 'min_humidity' in request.form:
            min_humidity = request.form['min_humidity']

        if 'max_humidity' in request.form:
            max_humidity = request.form['max_humidity']
        
        if 'lights_on' in request.form:
            lights_on = request.form['lights_on'] == 'on'

        if 'lights_on_time' in request.form:
            lights_on_time = request.form['lights_on_time']

        if 'lights_off_time' in request.form:
            lights_off_time = request.form['lights_off_time']

        grow.set_grow_settings(auto_mode=auto_mode,
                            humidifier_on=humidifier_on,
                            min_humidity=min_humidity,
                            max_humidity=max_humidity,
                            lights_on=lights_on,
                            lights_on_time=lights_on_time,
                            lights_off_time=lights_off_time)
        
    return redirect(url_for('index'))

@app.route('/m_dht_report/<temperature>/<humidity>', methods=['GET', 'POST'])
def sensor(temperature, humidity):
    grow.report_sensor_status(temperature=temperature, humidity=humidity)
    return f'temperature={str(temperature)} humidity={str(humidity)}'

@app.route('/m_humidifier_status/', methods=['GET'])
def humidifier_status():
    return str(int(grow.humidifier_on))

@app.route('/m_lights_status/', methods=['GET'])
def lights_status():
    return str(int(grow.lights_on))

##################################################################################################
@app.route('/plant', methods=['GET', 'POST'])
def plants():
    
    return render_template(
        'plant/index.html',
        plants=database.get_plants(),
        photoperiods=database.get_photoperiods(),
        genders=database.get_genders(),
        intensities=database.get_intensities()
    )

@app.route('/plant/create', methods=['GET', 'POST'])
def create_plant():
    if 'name' in request.form and 'date' in request.form and 'photoperiod_id' in request.form and 'gender_id' in request.form:
        database.insert_plant(request.form['name'], request.form['date'], request.form['photoperiod_id'], request.form['gender_id'])
    return redirect(url_for('plants'))

@app.route('/plant/update/<plant_id>', methods=['GET', 'POST'])
def update_plant(plant_id):
    if 'name' in request.form and 'date' in request.form and 'photoperiod_id' in request.form and 'gender_id' in request.form:
        database.update_plant(plant_id, request.form['name'], request.form['date'], request.form['photoperiod_id'], request.form['gender_id'])
    return redirect(url_for('plants'))

@app.route('/plant/delete/<plant_id>', methods=['GET', 'POST'])
def delete_plant(plant_id):
    database.delete_plant(plant_id)
    return redirect(url_for('plants'))
################################################################################################## 
@app.route('/watering/<plant_id>', methods=['GET', 'POST'])
def watering(plant_id):
    
    return render_template(
        'watering/index.html',
        plant_id=plant_id,
        waterings=database.get_plant_waterings(plant_id)
    )

@app.route('/watering/create/<plant_id>', methods=['GET', 'POST'])
def create_watering(plant_id):
    if 'date' in request.form and 'mililiter' in request.form:
        database.insert_watering(plant_id, request.form['date'], request.form['mililiter'])

    return redirect(url_for('watering', plant_id=plant_id))

@app.route('/watering/update/<plant_id>/<watering_id>', methods=['GET', 'POST'])
def update_watering(plant_id):
    # TODO: update watering
    return redirect(url_for('watering', plant_id=plant_id))

@app.route('/watering/delete/<plant_id>/<watering_id>', methods=['GET', 'POST'])
def delete_watering(plant_id, watering_id):
    database.delete_watering(watering_id)
    return redirect(url_for('watering', plant_id=plant_id))

################################################################################################## 
@app.route('/training/<plant_id>', methods=['GET', 'POST'])
def training(plant_id):
    
    return render_template(
        'training/index.html',
        trainings=database.get_plant_trainings(plant_id),
        training_types=database.get_training_types()
    )

@app.route('/training/create/<plant_id>', methods=['GET', 'POST'])
def create_training(plant_id):
    # TODO: create training
    return redirect(url_for('training', plant_id=plant_id))

@app.route('/training/update/<plant_id>', methods=['GET', 'POST'])
def update_training(plant_id):
    # TODO: update training
    return redirect(url_for('training', plant_id=plant_id))

@app.route('/training/delete/<plant_id>', methods=['GET', 'POST'])
def delete_training(plant_id):
    # TODO: delete training
    return redirect(url_for('training', plant_id=plant_id))


################################################################################################## 
@app.route('/feeding/<plant_id>', methods=['GET', 'POST'])
def feeding(plant_id):
    
    return render_template(
        'feeding/index.html',
        feedings=database.get_plant_feedings(plant_id)
    )

@app.route('/feeding/create/<plant_id>', methods=['GET', 'POST'])
def create_feeding(plant_id):
    # TODO: create feeding
    return redirect(url_for('feeding', plant_id=plant_id))

@app.route('/feeding/update/<plant_id>', methods=['GET', 'POST'])
def update_feeding(plant_id):
    # TODO: update feeding
    return redirect(url_for('feeding', plant_id=plant_id))

@app.route('/feeding/delete/<plant_id>', methods=['GET', 'POST'])
def delete_feeding(plant_id):
    # TODO: delete feeding
    return redirect(url_for('feeding', plant_id=plant_id))

################################################################################################## 
@app.route('/transplanting/<plant_id>', methods=['GET', 'POST'])
def transplanting(plant_id):
    
    return render_template(
        'transplanting/index.html',
        transplantings=database.get_plant_transplantings(plant_id)
    )

@app.route('/transplanting/create/<plant_id>', methods=['GET', 'POST'])
def create_transplanting(plant_id):
    # TODO: create transplanting
    return redirect(url_for('transplanting', plant_id=plant_id))

@app.route('/transplanting/update/<plant_id>', methods=['GET', 'POST'])
def update_transplanting(plant_id):
    # TODO: update transplanting
    return redirect(url_for('transplanting', plant_id=plant_id))

@app.route('/transplanting/delete/<plant_id>', methods=['GET', 'POST'])
def delete_transplanting(plant_id):
    # TODO: delete transplanting
    return redirect(url_for('transplanting', plant_id=plant_id))

################################################################################################## 
@app.route('/damage/<plant_id>', methods=['GET', 'POST'])
def damage(plant_id):
    
    return render_template(
        'damage/index.html',
        damages=database.get_plant_damages(plant_id),
        damage_types=database.get_damage_types(),
        intensities=database.get_intensities()
    )

@app.route('/damage/create/<plant_id>', methods=['GET', 'POST'])
def create_damage(plant_id):
    # TODO: create damage
    return redirect(url_for('damage', plant_id=plant_id))

@app.route('/damage/update/<plant_id>', methods=['GET', 'POST'])
def update_damage(plant_id):
    # TODO: update damage
    return redirect(url_for('damage', plant_id=plant_id))

@app.route('/damage/delete/<plant_id>', methods=['GET', 'POST'])
def delete_damage(plant_id):
    # TODO: delete damage
    return redirect(url_for('damage', plant_id=plant_id))
################################################################################################## 
@app.route('/harvest/<plant_id>', methods=['GET', 'POST'])
def harvest(plant_id):
    
    return render_template(
        'harvest/index.html',
        harvests=database.get_plant_harvests(plant_id)
    )

@app.route('/harvest/create/<plant_id>', methods=['GET', 'POST'])
def create_harvest(plant_id):
    # TODO: create harvest
    return redirect(url_for('harvest', plant_id=plant_id))

@app.route('/harvest/update/<plant_id>', methods=['GET', 'POST'])
def update_harvest(plant_id):
    # TODO: update harvest
    return redirect(url_for('harvest', plant_id=plant_id))

@app.route('/harvest/delete/<id>', methods=['GET', 'POST'])
def delete_harvest(plant_id):
    # TODO: delete harvest
    return redirect(url_for('harvest', plant_id=plant_id))


    
if __name__ == '__main__':
    print(app_config)
    app.run(host=app_config["host"], 
            port=app_config["port"], 
            debug=app_config["debug"])