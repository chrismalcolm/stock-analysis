# Consumer

## Summary
A Kafka producer which use historical stock price data from Yahoo Finance to publish as real-time stock data.

## Demo
insert video here

## How it works
* This script creates a **`Producer`** class which is able to publish JSON messages of stock price data to a Kafka topic.

* It collects the stock price data from **`Yahoo Finance`** using the yfinance module.

* The Producer class can be used as a **`Context Manager`** which enables a graceful startup and shutdown of the Kafka producer.

* Multiple producer can be run **`concurrently`**, each publishing data from different tickers.

* Tickers can be configured by changing the **`SYMBOLS`** list in the script.