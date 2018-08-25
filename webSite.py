import flask as f
import query_db
import random
import string
from model import app
from datetime import datetime
import dateutil.parser

db = query_db.Query()

@app.route('/')
def home():
    sensor=db.get_sensor()
    return f.render_template('home.html', sensor=sensor)

@app.route('/addThermostat',methods=['GET', 'POST'])
def addThermostat():
    if f.request.method == 'POST':
        url = f.request.form.get('url')
        room = f.request.form.get('room')
        error = db.add_sensor(url, room)
        if(error == "already existing url") | (error == "already existing room"):
            return f.render_template('addSensor.html', error="already existing url or room")
        if error == '404':
            return f.render_template('404.html')
        return f.redirect(f.url_for('home'))
    return f.render_template('addSensor.html')

@app.route('/removeThermostat/<idSensor>',methods=['GET', 'POST'])
def removeThermostat(idSensor):
    if f.request.method == 'POST':
         db.remove_sensor(idSensor)
         return f.redirect(f.url_for('home'))
    return f.render_template('home.html')


@app.route('/measurements/<idSensor>',methods=['GET', 'POST'])
def measurements(idSensor):
    url=db.get_url(idSensor)
    temp = db.get_last_measurement('temperature',url)
    hum = db.get_last_measurement('humidity',url)
    temp_min=db.get_min_measurement('temperature',url)
    temp_max=db.get_max_measurement('temperature',url)
    hum_min=db.get_min_measurement('humidity',url)
    hum_max=db.get_max_measurement('humidity',url)

    return f.render_template('dashboard.html', temp=temp, hum=hum, temp_min=temp_min,
                             temp_max=temp_max, hum_min=hum_min, hum_max=hum_max, idSensor=idSensor)


@app.route('/graphic/<idSensor>', methods=['GET', 'POST'])
def graphic(idSensor):

    if f.request.method == 'POST':
        url = db.get_url(idSensor)
        start_date = dateutil.parser.parse(f.request.form.get('datetime_start'))
        end_date = dateutil.parser.parse(f.request.form.get('datetime_stop'))

        if f.request.form.get('temperature') is not None:
            graph_data = db.read_measurement(start_date, end_date, 'temperature',url)

        if f.request.form.get('humidity') is not None:
            graph_data = db.read_measurement(start_date, end_date, 'humidity', url)

        graph_labels = db.get_times(start_date, end_date, url)
        return f.renderer_template('graphic.html', idSensor=idSensor )
    return f.render_template('graphic.html')


app.secret_key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(128))
#app.run(host='0.0.0.0', port=80)
app.run()
#127.0.0.1:5000