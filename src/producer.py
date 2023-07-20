import concurrent.futures
import json
import time
import pandas as pd
import yfinance as yf

from kafka import KafkaProducer

SERV_ADDR = "localhost:29092"
SYMBOLS = ["MSFT", "AAPL"]

# Kafka producer to be used as a context manager to stream stock data
class Producer:

    def __init__(self, serv_addr, topic, symbol):
        self.serv_addr = serv_addr
        self.topic = topic
        self.symbol = symbol
        self._producer = None

    def __enter__(self):
        # Initialise the Kafka producer
        self._producer = KafkaProducer(bootstrap_servers=self.serv_addr)
        return self

    def __exit__(self, type, value, traceback):
        # Close the Kafka producer
        self._producer.close()

    # Load the stock data and publish messages
    def run(self):

        # Raise an Expection if self._producer is not initialised
        if not self._producer:
            raise Exception("Producer has not been initialised")

        try:
            # Download and save 5 days worth of minute stock data
            # into a data frame
            self._print(f"({self.symbol}) Downloading stock data for {self.symbol}")
            df = yf.download(tickers=self.symbol, period="1d", interval="1m")

            # Insert column for timestamp into data
            start = int(time.time())
            end = int(start + df.shape[0])
            df.insert(0, "Timestamp", range(start, end), True)
            
            # Publish messages
            self._stream(df)
        
        except Exception as exc:
            self._print(f"({self.symbol}) Error: {exc}")
            raise exc

    def _stream(self, df):
        self._print(f"({self.symbol}) Streaming data")
        for _, row in df.iterrows():
            message = json.dumps(list(row.values))
            self._publish(message)
            time.sleep(1)

    def _publish(self, message):
        self._producer.send(self.topic, message.encode('utf-8'))
        self._print(f"({self.symbol}) Published: {message}")

    def _print(self, text):
        print(f"({self.symbol}) {text}")

# Stream data for the given ticker
def stream_data(symbol):
    topic = f"stock_data_{symbol.lower()}"
    with Producer(serv_addr=SERV_ADDR, topic=topic, symbol=symbol) as producer:
        producer.run()

def main():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(stream_data, sym): sym for sym in SYMBOLS}
        for future in concurrent.futures.as_completed(futures):
            future.result()

if __name__ == "__main__":
    main()