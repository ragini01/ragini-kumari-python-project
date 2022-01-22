import json
import pytest
import sqlite3
import time
import unittest
import requests

from app import app

class SensorRoutesTestCases(unittest.TestCase):

    def setUp(self):
        # Setup the SQLite DB
        conn = sqlite3.connect('test_database.db')
        conn.execute('DROP TABLE IF EXISTS readings')
        conn.execute('CREATE TABLE IF NOT EXISTS readings (device_uuid TEXT, type TEXT, value INTEGER, date_created INTEGER)')
        
        self.device_uuid = 'test_device'
        self.temperature_device_uuid = 'test_device_temperature'
        self.humidity_device_uuid = 'test_device_humidity'
        self.date_range_device_uuid = 'test_device_range'
        self.mode_device_uuid = 'test_device_mode'

        # Setup some sensor data
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.device_uuid, 'temperature', 22, int(time.time()) - 100))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.device_uuid, 'temperature', 50, int(time.time()) - 50))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.device_uuid, 'temperature', 100, int(time.time())))

        # temperature test rows
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.temperature_device_uuid, 'temperature', 22, int(time.time()) - 100))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.temperature_device_uuid, 'temperature', 50, int(time.time()) - 50))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.temperature_device_uuid, 'humidity', 100, int(time.time())))

         # humidity test rows
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.humidity_device_uuid, 'humidity', 22, int(time.time())))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.humidity_device_uuid, 'humidity', 55, int(time.time())))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.humidity_device_uuid, 'temperature', 11, int(time.time())))

        # date range test rows
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.date_range_device_uuid, 'temperature', 4, 1635335102))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.date_range_device_uuid, 'temperature', 22, 1635335111))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.date_range_device_uuid, 'temperature', 55, 1635335120))

        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    ('other_uuid', 'temperature', 22, int(time.time())))

        # mode test rows
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.mode_device_uuid, 'temperature', 22, int(time.time()) - 100))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.mode_device_uuid, 'temperature', 22, int(time.time()) - 50))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.mode_device_uuid, 'temperature', 100, int(time.time())))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.mode_device_uuid, 'temperature', 55, int(time.time()) - 100))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.mode_device_uuid, 'temperature', 55, int(time.time()) - 50))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.mode_device_uuid, 'temperature', 55, int(time.time())))
 
        conn.commit()

        app.config['TESTING'] = True

        self.client = app.test_client

    

    def test_device_readings_get(self):
        # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/{}/readings/'.format(self.device_uuid))

        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)
        

        # And the response data should have three sensor readings
        self.assertTrue(len(json.loads(request.data)) == 3)

    def test_device_readings_post(self):
        # Given a device UUID
        # When we make a request with the given UUID to create a reading with value > 100
        request = self.client().post('/devices/{}/readings/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'temperature',
                'value': 101
            }))
        # Then we should receive a 400
        self.assertEqual(request.status_code, 400)

        # When we make a request with the given UUID to create a reading with value < 0
        request = self.client().post('/devices/{}/readings/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'temperature',
                'value': -1
            }))
        # Then we should receive a 400
        self.assertEqual(request.status_code, 400)

        # When we make a request with the given UUID to create a reading with invalid type
        request = self.client().post('/devices/{}/readings/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'abcdef',
                'value': -1
            }))
        # Then we should receive a 400
        self.assertEqual(request.status_code, 400)

        # When we make a request with the given UUID to create a reading
        request = self.client().post('/devices/{}/readings/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'temperature',
                'value': 100
            }))

        # Then we should receive a 201
        self.assertEqual(request.status_code, 201)

        # And when we check for readings in the db
        conn = sqlite3.connect('test_database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('select * from readings where device_uuid="{}"'.format(self.device_uuid))
        rows = cur.fetchall()

        # We should have three
        self.assertTrue(len(rows) == 4)

    def test_device_readings_get_temperature(self):
        # Given a device UUID
        # When we make a request with the given UUID for type temperature
        request = self.client().get('/devices/{}/readings/?type={}'.format(self.temperature_device_uuid, 'temperature'))

        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        # And the response data should have three temperature sensor readings
        print(len(json.loads(request.data)))
        self.assertTrue(len(json.loads(request.data)) == 2)

    def test_device_readings_get_humidity(self):
        # Given a device UUID
        # When we make a request with the given UUID for type humidity
        request = self.client().get('/devices/{}/readings/?type={}'.format(self.humidity_device_uuid, 'humidity'))

        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        # And the response data should have two humidity sensor readings
        print(len(json.loads(request.data)))
        self.assertTrue(len(json.loads(request.data)) == 2)

    def test_device_readings_get_past_dates(self):
         # Given a device UUID
        # When we make a request with the given UUID for date range
        request = self.client().get('/devices/{}/readings/?start={}&&end={}'.format(self.date_range_device_uuid, 1635335102, 1635335111))

        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        # And the response data should have two sensor readings within the date range
        print(len(json.loads(request.data)))
        self.assertTrue(len(json.loads(request.data)) == 2)


    def test_device_readings_min(self):
         # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/{}/readings/min/'.format(self.device_uuid))

        # Then we should receive a 400 without sensor type
        self.assertEqual(request.status_code, 400)

        request = self.client().get('/devices/{}/readings/min/?type={}'.format(self.device_uuid, 'temperature'))
        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        # And the response data should have one sensor reading
        self.assertTrue(len(json.loads(request.data)) == 1)

        # And when we check for minimum value in the db
        conn = sqlite3.connect('test_database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('select * from readings where device_uuid="{}" and type="{}" order by value asc limit 1'.format(self.device_uuid, "temperature"))
        rows = cur.fetchall()

        # And the maximum value should be 100
        self.assertEqual(json.loads(request.data)[0]['value'], rows[0]['value'])

    def test_device_readings_max(self):
       # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/{}/readings/max/'.format(self.device_uuid))

        # Then we should receive a 400 without sensor type
        self.assertEqual(request.status_code, 400)

        request = self.client().get('/devices/{}/readings/max/?type={}'.format(self.device_uuid, 'temperature'))
        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        # And the response data should have one sensor reading
        self.assertTrue(len(json.loads(request.data)) == 1)

        # And when we check for minimum value in the db
        conn = sqlite3.connect('test_database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('select * from readings where device_uuid="{}" and type="{}" order by value desc limit 1'.format(self.device_uuid, "temperature"))
        rows = cur.fetchall()

        # And the maximum value should be 100
        self.assertEqual(json.loads(request.data)[0]['value'], rows[0]['value'])

    def test_device_readings_median(self):
        # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/{}/readings/median/'.format(self.device_uuid))

        # Then we should receive a 400 without sensor type
        self.assertEqual(request.status_code, 400)

        request = self.client().get('/devices/{}/readings/median/?type={}'.format(self.device_uuid, 'temperature'))
        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        # And the median value should be 50
        self.assertEqual(json.loads(request.data)['value'], 50)

    def test_device_readings_mean(self):
        # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/{}/readings/mean/'.format(self.device_uuid))

        # Then we should receive a 400 without sensor type
        self.assertEqual(request.status_code, 400)

        request = self.client().get('/devices/{}/readings/mean/?type={}'.format(self.device_uuid, 'temperature'))
        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        # And the mean value should be 57.333333333333336
        self.assertEqual(json.loads(request.data)['value'], 57.333333333333336)
    def test_device_readings_mode(self):
        # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/{}/readings/mode/'.format(self.mode_device_uuid))

        # Then we should receive a 400 without sensor type
        self.assertEqual(request.status_code, 400)

        request = self.client().get('/devices/{}/readings/mode/?type={}'.format(self.mode_device_uuid, 'temperature'))
        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        # And the mean value should be 57.333333333333336
        self.assertEqual(json.loads(request.data)['value'], 55)


    def test_device_readings_quartiles(self):
        # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/{}/readings/quartiles/'.format(self.date_range_device_uuid))
        # Then we should receive a 400 without sensor type
        self.assertEqual(request.status_code, 400)

        request = self.client().get('/devices/{}/readings/quartiles/?type={}'.format(self.date_range_device_uuid, 'temperature'))
        # Then we should receive a 400 without start date
        self.assertEqual(request.status_code, 400)

        request = self.client().get('/devices/{}/readings/quartiles/?type={}&&start={}'.format(self.date_range_device_uuid, 'temperature', 1635335102))
        # Then we should receive a 400 without end date
        self.assertEqual(request.status_code, 400)

        request = self.client().get('/devices/{}/readings/quartiles/?type={}&&start={}&&end={}'.format(self.date_range_device_uuid, 'temperature', 1635335102, 1635335120))
        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        # And the first quartile should be 13
        self.assertEqual(json.loads(request.data)['quartile_1'], 13)

        # And the third quartile should be 38.5
        self.assertEqual(json.loads(request.data)['quartile_3'], 38.5)

    def test_device_summary(self):
        # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/summary/')

        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        # And the response data should have six device summaries
        self.assertEqual(len(json.loads(request.data)), 6)

        # And the first one should be mode_device_uuid because of most readings
        self.assertEqual(json.loads(request.data)[0]['device_uuid'], self.mode_device_uuid)

        # And the last one should be other_uuid because of least readings
        self.assertEqual(json.loads(request.data)[len(json.loads(request.data)) - 1]['device_uuid'], 'other_uuid')

        # Most readings
        device_with_most_readings = json.loads(request.data)[0]
        # And its max reading value is
        self.assertEqual(device_with_most_readings['max_reading_value'], 100)
        # And its mean reading value is
        self.assertEqual(device_with_most_readings['mean_reading_value'], 51.5)
        # And its median reading value is
        self.assertEqual(device_with_most_readings['median_reading_value'], 55)
        # And its number of readings is
        self.assertEqual(device_with_most_readings['number_of_readings'], 6)
        # And its quartile 1 value is
        self.assertEqual(device_with_most_readings['quartile_1_value'], 30.25)
        # And its quartile 3 value is
        self.assertEqual(device_with_most_readings['quartile_3_value'], 55)