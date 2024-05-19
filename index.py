from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort, jsonify
from flask import Flask
from scripts.wind import Wind
from scripts.database import Database
from scripts.grow import Grow
import json
import sys
from pubsub import pub
import socket

app = Flask(__name__)
app.secret_key = '1234'

site = Blueprint('site', __name__, template_folder='templates')

with open(str(sys.argv[1])) as config_file:
    app_config = json.load(config_file)

database        = Database(path=app_config["database"], schema=app_config["schema"])
wind_controller = Wind(database=database)

grow = Grow()

##################################################################################################
@app.route("/")
def index():

    grow_data = grow.request_grow_data()

    temperature = grow_data['temperature']
    humidity = grow_data['humidity']

    return render_template('index.html', 
                           temperature=temperature,
                           humidity=humidity)

@app.route("/update-wind", methods=['GET','POST'])
def update_wind():
    
    if request.method == 'POST':
        if('auto_mode' in request.form and request.form['auto_mode'] == 'on'):
            wind_controller.set_auto(1)
        else:
            wind_controller.set_auto(0)

        if 'ventilation' in request.form:
            wind_controller.set_ventilation(request.form['ventilation'])

        if 'circulation' in request.form:
            wind_controller.set_circulation(request.form['circulation'])

        if 'act-time' in request.form:
            wind_controller.set_act_time(request.form['act_time'])

        if 'deact-time' in request.form:
            wind_controller.set_deact_time(request.form['deact_time'])
        
    return redirect(url_for('config'))


@app.route("/config", methods=['GET','POST'])
def config():
    return render_template('/config.html', 
                           auto=wind_controller.get_auto(),
                           circulation=wind_controller.get_circulation(),
                           ventilation=wind_controller.get_ventilation(),
                           act_time=wind_controller.get_act_time(),
                           deact_time=wind_controller.get_deact_time())

################################################################################################## 

if __name__ == '__main__':
    print(app_config)
    grow.start()
    app.run(host=app_config["host"], 
            port=app_config["port"], 
            debug=app_config["debug"])