# Canary Platform Homework

## Introduction
Imagine a system where hundreds of thousands of Canary like hardware devices are concurrently uploading temperature and humidty sensor data.

The API to facilitate this system accepts creation of sensor records, in addition to retrieval.

These `GET` and `POST` requests can be made at `/devices/<uuid>/readings/`.

Retrieval of sensor data should return a list of sensor values such as:

```
    [{
        'date_created': <int>,
        'device_uuid': <uuid>,
        'type': <string>,
        'value': <int>
    }]
```

The API supports optionally querying by sensor type, in addition to a date range.

A client can also access metrics such as the max, median and mean over a time range.

These metric requests can be made by a `GET` request to `/devices/<uuid>/readings/<metric>/`

When requesting max or median, a single sensor reading dictionary should be returned as seen above.

When requesting the mean, the response should be:

```
    {
        'value': <mean>
    }
```

The API also supports the retrieval of the 1st and 3rd quartile over a specific date range.

This request can be made via a `GET` to `/devices/<uuid>/readings/quartiles/` and should return

```
    {
        'quartile_1': <int>,
        'quartile_3': <int>
    }
```

Finally, the API supports a summary endpoint for all devices and readings. When making a `GET` request to this endpoint, we should receive a list of summaries as defined below, where each summary is sorted in descending order by number of readings per device.

```
    [
        {
            'device_uuid':<uuid>,
            'number_of_readings': <int>,
            'max_reading_value': <int>,
            'median_reading_value': <int>,
            'mean_reading_value': <int>,
            'quartile_1_value': <int>,
            'quartile_3_value': <int>
        },

        ... additional device summaries
    ]
```

The API is backed by a SQLite database.

## Getting Started
This service requires Python3. To get started, create a virtual environment using Python3.

Then, install the requirements using `pip install -r requirements.txt`.

Finally, run the API via `python app.py`.

## Testing
Tests can be run via `pytest -v`.

## Tasks
Your task is to fork this repo and complete the following:

- [Implemented] Add field validation. Only *temperature* and *humidity* sensors are allowed with values between *0* and *100*.
- [Implemented] Add logic for query parameters for *type* and *start/end* dates.
- [Implemented] Implementation
  - [Implemented] The max, median and mean endpoints.
  - [Implemented] The quartiles endpoint with start/end parameters
  - [Implemented] Add the path for the summary endpoint
  - [Implemented] Complete the logic for the summary endpoint
- [Implemented] Tests
  - [Implemented] Wrap up the stubbed out unit tests with your changes
  - [Implemented] Add tests for the new summary endpoint
  - [Implemented] Add unit tests for any missing error cases
- [ ] README
  - [ ] Explain any design decisions you made and why.
       [] Added functionalities for mode and min calculataions
       [] Added UnitTest funtion for summary endpoint
  - [ ] Imagine you're building the roadmap for this project over the next quarter. What features or updates would you suggest that we prioritize?
        Improvments:
        [] All the functions written inside app.py can be defined seprately (may be we can create controllers.py) and then call the functions in app.py while making HTTP requests
        [] In each of the HTTP call, we are interacting with DB where we are creating the connections and then executing the queries. Instead of this, we can create a seprate               folder for db where we can create db.py files to make the connection as well as for writing the db queries
        [] Some of the unit test codes are duplicate which can be reused 
        Roadmaps:
        [] We can make use of an orchestration tool (i.e docker) here so that the application can easily deployed and run in a containerized environment
        [] End points can be autenticated to make sure all the calls are secured (we can make use of a variety of API Gateways as solution)
        [] As the application grow going forward and frequency of data also gets increased , we can not rely on SQLLite db as well as Flask framework. Here, the alternatives can           be a timeseries db, any kind of data-streaming designs  or if we are still sticked to SQLLite db then we might need to think of certain factors like how can we                   optimize the db in terms of normalizations, splitting the table into small tables by adding constraints, adding functions like aggregations, indexing etc
        

When you're finished, send your git repo link to platform@canary.is. If you have any questions, please do not hesitate to reach out!
