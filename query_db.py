from urllib3 import exceptions
from model import db, Sensor, Measurement
import urllib3
import json
import datetime
from sqlalchemy.sql import func

def get_sensor_measure(url):   #fa una richiesta la prima volta che viene creato il sensore

    try:
        http = urllib3.PoolManager()
        r = http.request('GET', url)
        return json.loads(r.data.decode('utf-8'))
    except exceptions.RequestError:
        return None
    except exceptions.HTTPError:
        return None
    except ValueError:
        return None


class Query():

    def add_sensor(self,url,room):
        if self.check_existence_url(url)==True:
            error = 'already existing url'
            return error
        if self.check_existence_room(room)==True:
            error = 'already existing room'
            return error
        s = Sensor(url=url, room=room)
        data = get_sensor_measure(url)  #richiesta http per la prima volta quando viene aggiunto sensore
        if data == None:
            error = '404'
            return error
        else:
            db.session.add(s)
            db.session.commit()
            self.add_measurement(data['temp'], data['humidity'], url)

    def add_measurement(self, temperature, humidity, sensor_url):
        m = Measurement(temperature=temperature, humidity=humidity, sensor_url=sensor_url)
        db.session.add(m)
        db.session.commit()


    def read_measurement(self,datetime_start, datetime_stop, type, sensor_url):
        rm = Measurement.query.filter(db.and_((Measurement.datetime >=datetime_start), (Measurement.datetime <=datetime_stop), (Measurement.sensor_url==sensor_url)))
        values=[]
        for elem in rm:
            if type == 'humidity':
                values.append(elem.humidity)
            else:
                values.append(elem.temperature)
        return values


    def get_times(self,datetime_start,datetime_stop, sensor_url):
        rm = Measurement.query.filter(
            db.and_((Measurement.datetime >= datetime_start), (Measurement.datetime <= datetime_stop),
                    (Measurement.sensor_url == sensor_url)))
        values = []
        for elem in rm:
            values.append(elem.datetime.strftime("%Y-%m-%d %H:%M"))
        return values

    def get_last_measurement(self, type, sensor_url):
        lm = Measurement.query.order_by(Measurement.datetime.desc()).filter_by(sensor_url=sensor_url).all()
        if type == 'humidity':
            return lm[0].humidity, lm[0].datetime.strftime("%Y-%m-%d %H:%M")
        else:
            return lm[0].temperature,lm[0].datetime.strftime("%Y-%m-%d %H:%M")

    def get_min_measurement(self, type, sensor_url):
        mm = Measurement.query.filter(db.and_((Measurement.sensor_url == sensor_url),
                                              (Measurement.datetime.startswith(datetime.datetime.now().strftime("%Y-%m-%d"))))).all()
        values = []
        for elem in mm:
            if type == 'humidity':
                values.append(elem.humidity)
            else:
                values.append(elem.temperature)
        if not values:  #non sono state registrate misurazioni nella giornata
            return False
        minimum = min(values)
        return minimum

    def get_max_measurement(self, type, sensor_url):
        mM = Measurement.query.filter(db.and_((Measurement.sensor_url==sensor_url),
                                              (Measurement.datetime.startswith(datetime.datetime.now().strftime("%Y-%m-%d"))))).all()
        values = []
        for elem in mM:
            if type == 'humidity':
                values.append(elem.humidity)
            else:
                 values.append(elem.temperature)
        maximum = max(values)
        return maximum

    def get_sensorUrl(self):   #ritorna tutte le url in Sensor
        su = Sensor.query.all()
        urls = []
        for elem in su:
            urls.append(elem.url)
        return urls

    def get_sensorId(self):
        sId= Sensor.query.all()
        ids = []
        for elem in sId:
            ids.append(elem.id)
        return ids

    def get_sensor(self):
        s=Sensor.query.all()
        return s

    def get_url(selfs, id):
        s=Sensor.query.get(id)
        return (s.url)

    def check_existence_url(self,url):
        s=Sensor.query.filter_by(url=url).all()
        if s:  #se è vuota
            return True  #url non esiste
        else:
            return False

    def check_existence_room(self,room):
        s = Sensor.query.filter_by(room=room).all()
        if s:
            return True
        else:
            return False

    def remove_sensor(self, id):
        s = Sensor.query.filter_by(id=id).first()
        db.session.delete(s)
        db.session.commit()

    def read_measurement_today(self, date_time, type, url):
        #r=Measurement.query.filter(db.and_(Measurement.datetime==datetime.startswith(date_time),Measurement.url==url)).
        #(func.avg(Measurement.humidity).label('average'))

        #hour_=['00:00', '01:00', '02:00', '03:00','04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00','24:00']

        value=[]
        if type == 'humidity':
            r = db.session.query(func.avg(Measurement.humidity),Measurement.datetime).filter(db.and_(Measurement.datetime.startswith(date_time),Measurement.sensor_url==url)).group_by(func.extract('hour', Measurement.datetime)).all()
        else:
            r = db.session.query(func.avg(Measurement.temperature), Measurement.datetime).filter(db.and_(Measurement.datetime.startswith(date_time), Measurement.sensor_url == url)).group_by(func.extract('hour', Measurement.datetime)).all()
        for e in r:
            value.append(e[0])
        return value

    def read_hour(self,date_time,url):
        m=db.session.query(func.extract('hour', Measurement.datetime)).distinct(func.extract('hour', Measurement.datetime)).filter(db.and_(Measurement.datetime.startswith(date_time),Measurement.sensor_url==url)).all()
        values=[]
        for e in m:
            values.append(e[0])
        return values

#Query().read_measurement_today("2018-08-27","humidity","http://127.0.0.1:8082")
Query().read_hour("2018-08-27","http://127.0.0.1:8082")