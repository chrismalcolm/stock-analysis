# Consumer

## Summary
```bash
python3 src/consumer/main.py -h

usage: main.py [-h] symbols [symbols ...]

A Kafka consumer which subscribes to topics to receive real-time stock data events to save into a PostgreSQL Database.

positional arguments:
  symbols     stock symbols to consume messages for

options:
  -h, --help  show this help message and exit
```

## Demo
insert video here

## How it works
* This script creates a **`Consumer`** class which is able to subscribe to a Kafka topic to recieve JSON messages for stock price data.

* Once it reads this data, it saves the data to a **`PostgreSQL Database`** which can be used by the server.

* The Consumer class can be used as a **`Context Manager`** which enables a graceful startup and shutdown of the Kafka consumer.

* Multiple consumers can be run **`concurrently`**, in differet threads, each consuming data from different stocks.

* Configure the stocks to consume by changing the **`symbols`** argument.

