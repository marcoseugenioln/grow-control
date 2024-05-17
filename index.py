from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort, jsonify
from flask import Flask
from static.scripts.wind import Wind
from static.scripts.database import Database
import json
import sys

app = Flask(__name__)
app.secret_key = '1234'

site = Blueprint('site', __name__, template_folder='templates')

with open(str(sys.argv[1])) as config_file:
    config = json.load(config_file)

database        = Database(path=config["database"], schema=config["schema"])
wind_controller = Wind(database=database)

##################################################################################################
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/wind", methods=['GET','POST'])
def wind():
    return render_template('/wind/index.html', 
                           auto=wind_controller.get_auto(),
                           circulation=wind_controller.get_circulation(),
                           ventilation=wind_controller.get_ventilation(),
                           act_time=wind_controller.get_act_time(),
                           deact_time=wind_controller.get_deact_time())

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
        
    return redirect(url_for('wind'))


@app.route("/umidity", methods=['GET','POST'])
def umidity():
    return render_template('/umidity/index.html')

@app.route("/light", methods=['GET','POST'])
def light():
    return render_template('/light/index.html')

@app.route("/plant", methods=['GET','POST'])
def grow():
    return render_template('/plant/index.html')
################################################################################################## 

if __name__ == '__main__':
    print(config)
    app.run(host=config["host"], 
            port=config["port"], 
            debug=config["debug"])