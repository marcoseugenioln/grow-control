from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort, jsonify
from flask import Flask
# from scripts.database import Database
from scripts.grow import Grow
import json
import sys
from pubsub import pub

app = Flask(__name__)
app.secret_key = '1234'

site = Blueprint('site', __name__, template_folder='templates')

with open(str(sys.argv[1])) as config_file:
    app_config = json.load(config_file)

grow = Grow(ventilation_pin=app_config['ventilator_pin'], 
            circulation_pin=app_config['circulator_pin'], 
            dht_sensor_pin=app_config['dht_sensor_pin'], 
            humidifier_pin=app_config['humidifier_pin'],
            automatic=app_config['automatic'],
            ventilator_capacity=app_config['ventilator_capacity'],
            circulator_capacity=app_config['circulator_capacity'],
            desired_humidity=app_config['desired_humidity'],
            desired_temperature=app_config['desired_temperature'],
            humidity_toleration=app_config['humidity_toleration'])
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
                        humidifier_on=humidifier_on)
        
    return redirect(url_for('config'))

@app.route("/settings", methods=['GET','POST'])
def config():
    return render_template('/settings/index.html', 
                           auto_mode=grow.get_auto_mode(),
                           circulation=grow.circulator.get_capacity(),
                           ventilation=grow.ventilator.get_capacity(),
                           humidifier_on=grow.humidifier.is_active(),
                           desired_humidity=grow.desired_humidity,
                           desired_temperature=grow.desired_temperature)

##################################################################################################
# @app.route('/plant', methods=['GET', 'POST'])
# def plant():
    
#     return render_template(
#         'plant/index.html',
#         plants=,
#         photoperiods=,
#         trainings=,
#         training_types=,

#     )

################################################################################################## 

if __name__ == '__main__':
    print(app_config)
    grow.start()
    app.run(host=app_config["host"], 
            port=app_config["port"], 
            debug=app_config["debug"])