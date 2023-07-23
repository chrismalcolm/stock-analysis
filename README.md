# Stock Analysis
A collection of scripts for streaming and analysing **`Stock Price Data`**. Data is streamed concurrently using **`Kafka`** producers and consumers. There is also a **`Flask`** API with an endpoint to retrive stock price data from a **`PostgreSQL`** database. Stock price data is predicted using **`Artificial Inteligence`**. 

<img width="1485" alt="Screenshot 2023-07-23 at 17 48 55" src="https://github.com/chrismalcolm/stock-analysis/assets/43220741/99d4bd92-f023-4fc5-807e-ece72b6857ef">

## Prerequisites
**`python3`**, **`pip3`**, **`docker-compose`**

## Setup locally
Install required Python modules with correct versions.
```bash
pip3 install -r requirements.txt
```

Run PostgreSQL DB and Kafka Cluster locally in the background.
```bash
docker-compose up -d
```

Close down PostgreSQL DB and Kafka Cluster and remove volumes.
```bash
docker-compose down -v
```

Commands for each of the scripts that can be run.
```bash
# Run the Kafka producer
python3 src/producer/main.py

# Run the Kafka consumer
python3 src/consumer/main.py

# Run the Flask HTTP server
python3 src/server/main.py

# Run the stock price predictions AI
python3 src/prediction/main.py
```

## Docs
Documentation for each script is linked below.

* [Producer](https://github.com/chrismalcolm/stock-analysis/tree/main/src/producer/README.md)

* [Consumer](https://github.com/chrismalcolm/stock-analysis/tree/main/src/consumer/README.md)

* [Server](https://github.com/chrismalcolm/stock-analysis/tree/main/src/server/README.md)

* [Prediction](https://github.com/chrismalcolm/stock-analysis/tree/main/src/prediction/README.md)
