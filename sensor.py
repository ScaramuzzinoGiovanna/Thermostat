import urllib3
import time
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Measurement,Sensor
import datetime
from pytz import timezone
import sys
from urllib3 import exceptions

engine = create_engine('sqlite:////Users/Scara/PycharmProjects/Thermostat3/weatherdata.db')

DBSession = sessionmaker(bind=engine)
session = DBSession()

http = urllib3.PoolManager()


def get_data_arduino(url):

    try:
        r = http.request('GET', url)
        obj = json.loads(r.data.decode('utf-8'))
        newMeasurement = Measurement(temperature=obj['temp'], humidity=obj['humidity'],
                                     datetime=datetime.datetime.now().astimezone(timezone('Europe/Rome')),
                                     sensor_url=url)
        session.add(newMeasurement)
        session.commit()

    except exceptions.RequestError:
            print('Web site does not exist or it took too long to reach the URL:', url)
    except exceptions.HTTPError:
            print('httpError')
    except ValueError:
        print('Decoding JSON has failed')


def get_Sensor_url():
    sensors = session.query(Sensor).all()
    urls = []
    for elem in sensors:
       urls.append(elem.url)
    return urls


if __name__ == "__main__":
    while True:
        urls = get_Sensor_url()
        for u in urls:
            get_data_arduino(u)
        time.sleep(60)