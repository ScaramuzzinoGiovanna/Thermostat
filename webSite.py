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
    url = db.get_url(idSensor)
    temp,date_time = db.get_last_measurement('temperature',url)
    hum, date_time= db.get_last_measurement('humidity',url)
    temp_min = db.get_min_measurement('temperature',url)
    if temp_min==False:
        error = 'Non sono stati trovati risultati per oggi. Controllare che il termostato sia acceso.'
        return f.render_template('dashboard.html', temp=temp, hum=hum, date_time=date_time, error=error, idSensor=idSensor)
    temp_max = db.get_max_measurement('temperature',url)
    hum_min = db.get_min_measurement('humidity',url)
    hum_max = db.get_max_measurement('humidity',url)

    return f.render_template('dashboard.html', temp=temp, hum=hum, temp_min=temp_min,
                             temp_max=temp_max, hum_min=hum_min, hum_max=hum_max, idSensor=idSensor,date_time=date_time)


@app.route('/graphic/<idSensor>', methods=['GET', 'POST'])
def graphic(idSensor):
    url= db.get_url(idSensor)
    if f.request.method == 'POST':
        if f.request.form['option']=='temperature':
            if f.request.form['date'] == 'today':
                graph_data = db.read_measurement_today(datetime.now().strftime("%Y-%m-%d"), 'temperature', url)
                print(graph_data)

        if f.request.form['option']=='humidity':
            if f.request.form['date']=='today':
                graph_data = db.read_measurement_today(datetime.now().strftime("%Y-%m-%d"), 'humidity', url)

        graph_label = db.read_hour(datetime.now().strftime("%Y-%m-%d"),url)
        return f.render_template('graphic.html', idSensor=idSensor,data=graph_data,labels=graph_label)
    return f.render_template('graphic.html',idSensor=idSensor)



app.secret_key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(128))
#app.run(host='0.0.0.0', port=80)
app.run()
#127.0.0.1:5000