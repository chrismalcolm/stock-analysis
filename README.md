# Stock Analysis

## producer.py
A Kafka producer which use historical stock data from Yahoo Finance to publish as real-time stock data.

## consumer.py
A Kafka consumer which subscribes to topics to receive real-time stock data events to save into a Postgres DB.

## server.py
A Flash HTTP server to handle requests for stock data which can be filtered and aggregated for analysis or front-end client visuals.