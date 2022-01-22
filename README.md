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

- [ ] Add field validation. Only *temperature* and *humidity* sensors are allowed with values between *0* and *100*.
- [ ] Add logic for query parameters for *type* and *start/end* dates.
- [ ] Implementation
  - [ ] The max, median and mean endpoints.
  - [ ] The quartiles endpoint with start/end parameters
  - [ ] Add the path for the summary endpoint
  - [ ] Complete the logic for the summary endpoint
- [ ] Tests
  - [ ] Wrap up the stubbed out unit tests with your changes
  - [ ] Add tests for the new summary endpoint
  - [ ] Add unit tests for any missing error cases
- [ ] README
  - [ ] Explain any design decisions you made and why.
  - [ ] Imagine you're building the roadmap for this project over the next quarter. What features or updates would you suggest that we prioritize?

When you're finished, send your git repo link to platform@canary.is. If you have any questions, please do not hesitate to reach out!
