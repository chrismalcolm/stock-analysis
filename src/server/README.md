# Server

## Summary
```
python3 src/server/main.py -h

usage: main.py [-h] [-H HOST] [-p PORT]

A Flash HTTP server to handle requests for
stock data which can be used for analysis
or front-end client visuals.

options:
  -h, --help          show this help
                      message and exit
  -H HOST, --host HOST
                      host ip
  -p PORT, --port PORT
                      port of the API
                      server
```

## Demo
https://github.com/chrismalcolm/stock-analysis/assets/43220741/a66019b1-4990-47ac-9db3-05ee25108d86

## How it works
* This script runs **`Flask HTTP server`** on a specified or default host and port.

* It contains two endpoints **`GET /data`** and **`POST /data`**. Both can be used to return **`filtered`**  and **`aggregated`** 
 stock price data from the **`PostgreSQL Database`**.

* Data is filtered by specifying the **`symbols`** 
, **`metrics`**, **`start`** and **`end`** parameters.

* If 'timestamp' is present in the metrics, then **`timeseries`** data will be returned.

* If 'timestamp' is not present in the metrics, then **`aggregated`** data will be returned.

