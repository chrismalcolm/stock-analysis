# Stock Analysis
A collection of scripts working with stock data.

## Prerequisites
**`python`**, **`docker`**

## Setup locally
Setup python3 venv using the module versions listed in `requirements.txt`.

Run PostgreSQL DB and Kafka Cluster locally.
```bash
docker compose up -d
```

Close down PostgreSQL DB and Kafka Cluster
```bash
docker compose down -v
```

## src

### **producer.py**
A Kafka producer which use historical stock data from Yahoo Finance to publish as real-time stock data.

### **consumer.py**
A Kafka consumer which subscribes to topics to receive real-time stock data events to save into a Postgres DB.

### **server.py**
A Flash HTTP server to handle requests for stock data which can be used for analysis or front-end client visuals.

### **predictions.py**
Predict the closing stock price using the artficial recurrent neural network Long Short Term Memory (LSTM).