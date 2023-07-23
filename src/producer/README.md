# Producer

## Summary
```
python3 src/producer/main.py -h

usage: main.py [-h] symbols [symbols ...]

A Kafka producer which use historical stock price data
from Yahoo Finance to publish as real-time stock data.

positional arguments:
  symbols     stock symbols to produce messages for

options:
  -h, --help  show this help message and exit
```

## Demo
https://github.com/chrismalcolm/stock-analysis/assets/43220741/1fa82581-5797-4f56-84c7-939c4a8f1613

## How it works
* This script creates a **`Producer`** class which is able to publish JSON messages of stock price data to a Kafka topic.

* It collects the stock price data from **`Yahoo Finance`** using the yfinance module.

* The Producer class can be used as a **`Context Manager`** which enables a graceful startup and shutdown of the Kafka producer.

* Multiple producer can be run **`concurrently`**, each publishing data from different tickers.

* Configure the stocks to produce for by changing the **`symbols`** argument.
