from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort, jsonify
from flask import Flask
from scripts.grow import Grow
from scripts.database import Database
import json
import sys
from pubsub import pub

app = Flask(__name__)
app.secret_key = '1234'

site = Blueprint('site', __name__, template_folder='templates')

with open(str(sys.argv[1])) as config_file:
    app_config = json.load(config_file)

database = Database(database_path='database/schema.db', schema_file='database/schema.sql')

grow = Grow(ventilator_pin=app_config['ventilator_pin'], 
            circulator_pin=app_config['circulator_pin'], 
            dht_sensor_pin=app_config['dht_sensor_pin'], 
            humidifier_pin=app_config['humidifier_pin'],
            heater_pin=app_config['heater_pin'],
            automatic=app_config['automatic'],
            ventilator_capacity=app_config['ventilator_capacity'],
            circulator_capacity=app_config['circulator_capacity'],
            desired_humidity=app_config['desired_humidity'],
            desired_temperature=app_config['desired_temperature'],
            humidity_tolerance=app_config['humidity_tolerance'])

##################################################################################################
@app.route("/")
def index():
    return render_template('index.html', 
                           temperature=grow.temperature,
                           humidity=grow.humidity,
                           ventilation_capacity=grow.ventilator.get_capacity(),
                           circulation_capacity=grow.circulator.get_capacity(),
                           humidifier_on = grow.humidifier.is_active())

@app.route("/settings-cmd", methods=['GET','POST'])
def grow_settings_cmd():
    
    if request.method == 'POST':

        auto_mode = False
        desired_humidity = 0
        desired_temperature = 0
        light_act_time = None
        light_deact_time = None
        humidifier_on = False
        heater_on = False
        ventilation = 0
        circulation = 0

        if 'auto_mode' in request.form:
            auto_mode = request.form['auto_mode'] == 'on'

        if 'desired_humidity' in request.form:
            desired_humidity = request.form['desired_humidity']

        if 'desired_temperature' in request.form:
            desired_temperature = request.form['desired_temperature']

        if 'light_act_time' in request.form:
            light_act_time = request.form['light_act_time']

        if 'light_deact_time' in request.form:
            light_deact_time = request.form['light_deact_time']

        if 'humidifier_on' in request.form:
            humidifier_on = request.form['humidifier_on'] == 'on'

        if 'heater_on' in request.form:
            heater_on = request.form['heater_on'] == 'on'

        if 'ventilation' in request.form:
            ventilation = request.form['ventilation']

        if 'circulation' in request.form:
            circulation = request.form['circulation']

        pub.sendMessage('m_grow_settings_cmd', 
                        auto_mode=auto_mode,
                        desired_humidity=desired_humidity,
                        desired_temperature=desired_temperature,
                        light_act_time=light_act_time,
                        light_deact_time=light_deact_time, 
                        ventilation_capacity=ventilation, 
                        circulation_capacity=circulation, 
                        humidifier_on=humidifier_on,
                        heater_on=heater_on)
        
    return redirect(url_for('config'))

@app.route("/settings", methods=['GET','POST'])
def config():
    return render_template('/settings/index.html', 
                           auto_mode=grow.get_auto_mode(),
                           circulation=grow.circulator.get_capacity(),
                           ventilation=grow.ventilator.get_capacity(),
                           humidifier_on=grow.humidifier.is_active(),
                           heater_on=grow.heater.is_active(),
                           desired_humidity=grow.desired_humidity,
                           desired_temperature=grow.desired_temperature)


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

@app.route('/plant/update/<id>', methods=['GET', 'POST'])
def update_plant(id):
    # TODO: update plant
    if 'name' in request.form and 'date' in request.form and 'photoperiod_id' in request.form and 'gender_id' in request.form:
        database.update_plant(id, request.form['name'], request.form['date'], request.form['photoperiod_id'], request.form['gender_id'])
    return redirect(url_for('plant'))

@app.route('/plant/delete/<id>', methods=['GET', 'POST'])
def delete_plant(id):
    # TODO: delete plant
    database.delete_plant(id)
    return redirect(url_for('plants'))
################################################################################################## 
@app.route('/watering/<id>', methods=['GET', 'POST'])
def watering(id):
    
    return render_template(
        'watering/index.html',
        waterings=database.get_plant_waterings(id)
    )

@app.route('/watering/create/<id>', methods=['GET', 'POST'])
def create_watering(id):
    # TODO: create watering
    return redirect(url_for('watering', id=id))

@app.route('/watering/update/<id>', methods=['GET', 'POST'])
def update_watering(id):
    # TODO: update watering
    return redirect(url_for('watering', id=id))

@app.route('/watering/delete/<id>', methods=['GET', 'POST'])
def delete_watering(id):
    # TODO: delete watering
    return redirect(url_for('watering', id=id))

################################################################################################## 
@app.route('/training/<id>', methods=['GET', 'POST'])
def training(id):
    
    return render_template(
        'training/index.html',
        trainings=database.get_plant_trainings(id),
        training_types=database.get_training_types()
    )

@app.route('/training/create/<id>', methods=['GET', 'POST'])
def create_training(id):
    # TODO: create training
    return redirect(url_for('training', id=id))

@app.route('/training/update/<id>', methods=['GET', 'POST'])
def update_training(id):
    # TODO: update training
    return redirect(url_for('training', id=id))

@app.route('/training/delete/<id>', methods=['GET', 'POST'])
def delete_training(id):
    # TODO: delete training
    return redirect(url_for('training', id=id))


################################################################################################## 
@app.route('/feeding/<id>', methods=['GET', 'POST'])
def feeding(id):
    
    return render_template(
        'feeding/index.html',
        feedings=database.get_plant_feedings(id)
    )

@app.route('/feeding/create/<id>', methods=['GET', 'POST'])
def create_feeding(id):
    # TODO: create feeding
    return redirect(url_for('feeding', id=id))

@app.route('/feeding/update/<id>', methods=['GET', 'POST'])
def update_feeding(id):
    # TODO: update feeding
    return redirect(url_for('feeding', id=id))

@app.route('/feeding/delete/<id>', methods=['GET', 'POST'])
def delete_feeding(id):
    # TODO: delete feeding
    return redirect(url_for('feeding', id=id))

################################################################################################## 
@app.route('/transplanting/<id>', methods=['GET', 'POST'])
def transplanting(id):
    
    return render_template(
        'transplanting/index.html',
        transplantings=database.get_plant_transplantings(id)
    )

@app.route('/transplanting/create/<id>', methods=['GET', 'POST'])
def create_transplanting(id):
    # TODO: create transplanting
    return redirect(url_for('transplanting', id=id))

@app.route('/transplanting/update/<id>', methods=['GET', 'POST'])
def update_transplanting(id):
    # TODO: update transplanting
    return redirect(url_for('transplanting', id=id))

@app.route('/transplanting/delete/<id>', methods=['GET', 'POST'])
def delete_transplanting(id):
    # TODO: delete transplanting
    return redirect(url_for('transplanting', id=id))

################################################################################################## 
@app.route('/damage/<id>', methods=['GET', 'POST'])
def damage(id):
    
    return render_template(
        'damage/index.html',
        damages=database.get_plant_damages(id),
        damage_types=database.get_damage_types(),
        intensities=database.get_intensities()
    )

@app.route('/damage/create/<id>', methods=['GET', 'POST'])
def create_damage(id):
    # TODO: create damage
    return redirect(url_for('damage', id=id))

@app.route('/damage/update/<id>', methods=['GET', 'POST'])
def update_damage(id):
    # TODO: update damage
    return redirect(url_for('damage', id=id))

@app.route('/damage/delete/<id>', methods=['GET', 'POST'])
def delete_damage(id):
    # TODO: delete damage
    return redirect(url_for('damage', id=id))
################################################################################################## 
@app.route('/harvest/<id>', methods=['GET', 'POST'])
def harvest(id):
    
    return render_template(
        'harvest/index.html',
        harvests=database.get_plant_harvests(id)
    )

@app.route('/harvest/create/<id>', methods=['GET', 'POST'])
def create_harvest(id):
    # TODO: create harvest
    return redirect(url_for('harvest', id=id))

@app.route('/harvest/update/<id>', methods=['GET', 'POST'])
def update_harvest(id):
    # TODO: update harvest
    return redirect(url_for('harvest', id=id))

@app.route('/harvest/delete/<id>', methods=['GET', 'POST'])
def delete_harvest(id):
    # TODO: delete harvest
    return redirect(url_for('harvest', id=id))

if __name__ == '__main__':
    print(app_config)
    grow.start()
    app.run(host=app_config["host"], 
            port=app_config["port"], 
            debug=app_config["debug"])