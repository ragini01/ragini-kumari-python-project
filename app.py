from flask import Flask, render_template, request, Response
from flask.json import jsonify
import json
import sqlite3
import time
import statistics
import numpy as np

app = Flask(__name__)

# Setup the SQLite DB
conn = sqlite3.connect('database.db')
conn.execute(
    'CREATE TABLE IF NOT EXISTS readings (device_uuid TEXT, type TEXT, value INTEGER, date_created INTEGER)')
conn.close()

# Function for DB queries
def request_query(device_uuid, sensor_type, start_time, end_time):
    # db query
    query = 'select * from readings where device_uuid="' + device_uuid + '"'.format(device_uuid)
    if sensor_type is not None:
        query += ' and type = "' + sensor_type + '"'
    if start_time is not None:
        query += ' and date_created >= "' + start_time + '"'
    if end_time is not None:
        query += ' and date_created <= "' + end_time + '"'
    return query

def request_summary_query(sensor_type, start_time, end_time):
    # db query to get the summary
    query = 'select device_uuid, value from readings'
    if sensor_type is None and start_time is None and end_time is None:
        return query
    query += ' where'
    if sensor_type is not None:
        query += ' type = "' + sensor_type + '" and'
    if start_time is not None:
        query += ' date_created >= "' + start_time + '" and'
    if end_time is not None:
        query += ' date_created <= "' + end_time + '" and'
    query = query[: len(query) - 4]
    return query    


@app.route('/devices/<string:device_uuid>/readings/', methods=['POST', 'GET'])
def request_device_readings(device_uuid):
    """
    This endpoint allows clients to POST or GET data specific sensor types.

    POST Parameters:
    * type -> The type of sensor (temperature or humidity)
    * value -> The integer value of the sensor reading
    * date_created -> The epoch date of the sensor reading.
        If none provided, we set to now.

    Optional Query Parameters:
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    * type -> The type of sensor value a client is looking for
    """
    try:
        # Set the db that we want and open the connection
        if app.config['TESTING']:
            conn = sqlite3.connect('test_database.db')
        else:
            conn = sqlite3.connect('database.db')
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

        if request.method == 'POST':
            # Grab the post parameters
            post_data = json.loads(request.data)
            sensor_type = post_data.get('type')
            value = post_data.get('value')

            # Added Field validation
            if sensor_type is None or sensor_type not in ['temperature', 'humidity']:
                return 'Bad Request', 400
            if value is None or value < 0 or value > 100:
                return 'Bad Request', 400

            date_created = post_data.get('date_created', int(time.time()))

            # Insert data into db
            cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (device_uuid, sensor_type, value, date_created))

            conn.commit()

            # Return success
            return 'success', 201
        else:
            # Get optional query parameters
            start_time = request.args.get('start')
            end_time = request.args.get('end')
            sensor_type = request.args.get('type')

        # Generate query
        query = request_query(device_uuid, sensor_type, start_time, end_time)
        # Execute the query
        cur.execute(query)
        rows = cur.fetchall()

        # Return the JSON
        return jsonify([dict(zip(['device_uuid', 'type', 'value', 'date_created'], row)) for row in rows]), 200
    except Exception:
        return 'Server Error', 500


@app.route('/devices/<string:device_uuid>/readings/max/', methods=['GET'])
def request_device_readings_max(device_uuid):
    """
    This endpoint allows clients to GET the max sensor reading for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for

    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    try:
        # Set the db that we want and open the connection
        if app.config['TESTING']:
            conn = sqlite3.connect('test_database.db')
        else:
            conn = sqlite3.connect('database.db')
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

        # Get query parameters
        sensor_type = request.args.get('type')
        if sensor_type is None:
            return 'Bad Request', 400

        start_time = request.args.get('start')
        end_time = request.args.get('end')

        # Generate query
        query = request_query(device_uuid, sensor_type, start_time, end_time)
        # Get max value from db
        query += ' order by value desc limit 1'

        # Execute the query
        cur.execute(query)
        rows = cur.fetchall()


        # Return the JSON
        return jsonify([dict(zip(['device_uuid', 'type', 'value', 'date_created'], row)) for row in rows]), 200
    except Exception:
        return 'Server Error', 500


@app.route('/devices/<string:device_uuid>/readings/median/', methods=['GET'])
def request_device_readings_median(device_uuid):
    """
    This endpoint allows clients to GET the median sensor reading for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for

    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    try:
        # Set the db that we want and open the connection
        if app.config['TESTING']:
            conn = sqlite3.connect('test_database.db')
        else:
            conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Get query parameters
        sensor_type = request.args.get('type')
        if sensor_type is None:
            return 'Bad Request', 400

        start_time = request.args.get('start')
        end_time = request.args.get('end')

        # Generate query
        query = request_query(device_uuid, sensor_type, start_time, end_time)

        # Execute the query
        cur.execute(query)
        rows = cur.fetchall()

        if len(rows) == 0:
            return 'No records found', 200

        # Calculate the median
        values = [row['value'] for row in rows]
        numpy_array = np.array(values)
        median_value = np.quantile(numpy_array, .5) # return 50th percentile, i.e. median.

        values = [row['date_created'] for row in rows]
        numpy_array = np.array(values)
        median_date = np.quantile(numpy_array, .5) # return 50th percentile, i.e. median.

        return jsonify({"date_created": median_date, "device_uuid": device_uuid, "type": sensor_type, "value": median_value}), 200
    except Exception:
        return 'Server Error', 500


@app.route('/devices/<string:device_uuid>/readings/mean/', methods=['GET'])
def request_device_readings_mean(device_uuid):
    """
    This endpoint allows clients to GET the mean sensor readings for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for

    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    try:
        # Set the db that we want and open the connection
        if app.config['TESTING']:
            conn = sqlite3.connect('test_database.db')
        else:
            conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Get query parameters
        sensor_type = request.args.get('type')
        if sensor_type is None:
            return 'Bad Request', 400

        start_time = request.args.get('start')
        end_time = request.args.get('end')

        # Generate query
        query = request_query(device_uuid, sensor_type, start_time, end_time)

        # Execute the query
        cur.execute(query)
        rows = cur.fetchall()
        if len(rows) == 0:
            return 'No records found', 200

        # Calculate the mean
        sum = 0
        for row in rows:
            sum += row[2]
        mean = sum/len(rows)

        # Return the JSON
        return jsonify({"value": mean}), 200
    except Exception:
        return 'Server Error', 500



@app.route('/devices/<string:device_uuid>/readings/quartiles/', methods=['GET'])
def request_device_readings_quartiles(device_uuid):
    """
    This endpoint allows clients to GET the 1st and 3rd quartile
    sensor reading value for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    try:
        # Set the db that we want and open the connection
        if app.config['TESTING']:
            conn = sqlite3.connect('test_database.db')
        else:
            conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Get query parameters
        sensor_type = request.args.get('type')
        if sensor_type is None:
            return 'Bad Request', 400
        start_time = request.args.get('start')
        if start_time is None:
            return 'Bad Request', 400
        end_time = request.args.get('end')
        if end_time is None:
            return 'Bad Request', 400

        # Generate query
        query = request_query(device_uuid, sensor_type, start_time, end_time)

        # Execute the query
        cur.execute(query)
        rows = cur.fetchall()

        if len(rows) == 0:
            return 'No records found', 200
        # Calculate quartiles
        values = [row['value'] for row in rows]
        numpy_array = np.array(values)
        print(numpy_array)
        quartiles = np.quantile(numpy_array, [.25, .75]) # return 1st and 3rd quartiles

        # Return the JSON
        return jsonify({"quartile_1": quartiles[0], "quartile_3": quartiles[1]}), 200
    except Exception:
        return 'Server Error', 500


@app.route('/devices/summary/', methods=['GET'])
def request_readings_summary():
    """
    This endpoint allows clients to GET a full summary
    of all sensor data in the database per device.

    Optional Query Parameters
    * type -> The type of sensor value a client is looking for
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    try:
        # Set the db that we want and open the connection
        if app.config['TESTING']:
            conn = sqlite3.connect('test_database.db')
        else:
            conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Get query parameters
        sensor_type = request.args.get('type')
        start_time = request.args.get('start')
        end_time = request.args.get('end')

        # Generate query
        query = request_readings_summary(sensor_type, start_time, end_time)

        # Execute the query
        cur.execute(query)
        rows = cur.fetchall()

        device_values_dict = {}
        for row in rows:
            if row[0] not in device_values_dict:
                device_values_dict[row[0]] = []
            device_values_dict[row[0]].append(row[1])

        # Generate the summary
        summary_list = []
        for device_id in device_values_dict:
            summary_dict = {}
            numpy_array = np.array(device_values_dict[device_id])
            summary_dict['device_uuid'] = device_id
            summary_dict['number_of_readings'] = len(device_values_dict[device_id])
            summary_dict['max_reading_value'] = max(device_values_dict[device_id])
            summary_dict['median_reading_value'] = np.quantile(numpy_array, .5)
            summary_dict['mean_reading_value'] = statistics.mean(device_values_dict[device_id])
            summary_dict['quartile_1_value'] = np.quantile(numpy_array, .25)
            summary_dict['quartile_3_value'] = np.quantile(numpy_array, .75)
            summary_list.append(summary_dict)
        summary_list = sorted(summary_list, key=lambda k: k['number_of_readings'], reverse=True)
        return jsonify(summary_list), 200
    except Exception:
        return 'Server Error', 500

@app.route('/devices/<string:device_uuid>/readings/min/', methods = ['GET'])
def request_device_readings_min(device_uuid):
    """
    This endpoint allows clients to GET the min sensor reading for a device.
    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for
    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """
    try:
        # Set the db that we want and open the connection
        if app.config['TESTING']:
            conn = sqlite3.connect('test_database.db')
        else:
            conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Get query parameters
        sensor_type = request.args.get('type')
        if sensor_type is None:
            return 'Bad Request', 400

        start_time = request.args.get('start')
        end_time = request.args.get('end')

        # Generate query
        query = request_query(device_uuid, sensor_type, start_time, end_time)
        # Get min value from db
        query += ' order by value asc limit 1'

        # Execute the query
        cur.execute(query)
        rows = cur.fetchall()


        # Return the JSON
        return jsonify([dict(zip(['device_uuid', 'type', 'value', 'date_created'], row)) for row in rows]), 200
    except Exception:
        return 'Server Error', 500

@app.route('/devices/<string:device_uuid>/readings/mode/', methods = ['GET'])
def request_device_readings_mode(device_uuid):
    """
    This endpoint allows clients to GET the mode sensor readings for a device.
    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for
    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    try:
        # Set the db that we want and open the connection
        if app.config['TESTING']:
            conn = sqlite3.connect('test_database.db')
        else:
            conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Get query parameters
        sensor_type = request.args.get('type')
        if sensor_type is None:
            return 'Bad Request', 400

        start_time = request.args.get('start')
        end_time = request.args.get('end')

        # Generate query
        query = request_query(device_uuid, sensor_type, start_time, end_time)

        # Execute the query
        cur.execute(query)
        rows = cur.fetchall()
        if len(rows) == 0:
            return 'No records found', 200

        # Calculate the mode
        mode_list = []
        for row in rows:
            mode_list.append(row[2])
        print(mode_list)
        mode = statistics.mode(mode_list)
        print(mode)

        # Return the JSON
        return jsonify({"value": mode}), 200
    except:
        return 'Server Error', 500


if __name__ == '__main__':
    app.run()
