# Producer

## Summary
A Kafka producer which pu to topics to receive real-time stock data events to save into a PostgreSQL Database.

## Demo
insert video here

## How it works
* This script creates a **`Consumer`** class which is able to subscribe to a Kafka topic to recieve JSON messages for stock price data.

* Once it reads this data, it saves the data to a **`PostgreSQL Database`** which can be used by the server.

* The Consumer class can be used as a **`Context Manager`** which enables a graceful startup and shutdown of the Kafka consumer.

* Multiple consumers can be run **`concurrently`**, each consuming data from different tickers.

* Tickers can be configured by changing the **`SYMBOLS`** list in the script.

