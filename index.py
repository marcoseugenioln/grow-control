from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort, jsonify
from flask import Flask
from scripts.wind import Wind
from scripts.database import Database
from scripts.grow import Grow
import json
import sys
from pubsub import pub

app = Flask(__name__)
app.secret_key = '1234'

site = Blueprint('site', __name__, template_folder='templates')

with open(str(sys.argv[1])) as config_file:
    app_config = json.load(config_file)

grow = Grow()
##################################################################################################
@app.route("/")
def index():

    dht_data = grow.request_dht_data()
    return render_template('index.html', 
                           temperature=dht_data['temperature'],
                           humidity=dht_data['humidity'],
                           ventilation_capacity=grow.wind.get_ventilation(),
                           circulation_capacity=grow.wind.get_circulation())

@app.route("/wind-config-cmd", methods=['GET','POST'])
def wind_config_cmd():
    
    if request.method == 'POST':

        automatic_mode = 0
        ventilation = 0
        circulation = 0
        activation_time = None
        deactivation_time = None
        
        if('auto_mode' in request.form):
            automatic_mode = int(request.form['auto_mode'] == 'on')

        if 'ventilation' in request.form:
            ventilation = request.form['ventilation']

        if 'circulation' in request.form:
            circulation = request.form['circulation']

        if 'act-time' in request.form:
            activation_time=request.form['act_time']

        if 'deact-time' in request.form:
            deactivation_time=request.form['deact_time']

        pub.sendMessage('m_wind_config_cmd', 
                        automatic_mode=automatic_mode,
                        ventilation=ventilation,
                        circulation=circulation,
                        activation_time=activation_time,
                        deactivation_time=deactivation_time)
        
    return redirect(url_for('config'))


@app.route("/config", methods=['GET','POST'])
def config():
    return render_template('/config.html', 
                           auto=grow.wind.get_automatic_mode(),
                           circulation=grow.wind.get_circulation(),
                           ventilation=grow.wind.get_ventilation(),
                           act_time=grow.wind.get_activation_time(),
                           deact_time=grow.wind.get_deactivation_time(),
                           humidifier_on = grow.humidifier.is_active(),
                           humidifier_auto = grow.humidifier.get_automatic_mode())

@app.route("/humidifier-cmd", methods=['GET','POST'])
def humidifier_cmd():

    manual_activation = False
    automatic_mode = False

    if 'active' in request.form:
        manual_activation = request.form['active'] == 'on'
    if 'auto-mode' in request.form:
        automatic_mode = request.form['auto-mode'] == 'on'
    
    pub.sendMessage('m_humidifier_cmd', automatic_mode=automatic_mode, on=manual_activation)

    return redirect(url_for('config'))

################################################################################################## 

if __name__ == '__main__':
    print(app_config)
    grow.start()
    app.run(host=app_config["host"], 
            port=app_config["port"], 
            debug=app_config["debug"])