import argparse
import concurrent.futures
import json
import psycopg2

from dotenv import dotenv_values
from kafka import KafkaConsumer


class Consumer:
    """Kafka consumer to read stock price data."""

    def __init__(self, config, topic, symbol):
        self.serv_addr = config["KAFKA_SERV_ADDR"]
        self.group_id = config["KAFKA_GROUP_ID"]
        self.topic = topic
        self.symbol = symbol
        self._conn = None
        self._consumer = None

    def __enter__(self):
        # Initialise the Postgres connection
        self._conn = self._connect_db(config)
        # Initialise the Kafka consumer
        self._consumer = KafkaConsumer(
            self.topic, 
            group_id=self.group_id, 
            bootstrap_servers=self.serv_addr
        )
        return self

    def __exit__(self, type, value, traceback):
        # Close DB connection
        self._conn.close()
        # Close the Kafka consumer
        self._consumer.close()

    def run(self):
        """Consume messages from a Kafka topic."""

        # Raise an Expection if self._conn is not initialised
        if self._conn is None:
            raise Exception("Database connection has not been initialised")

        # Raise an Expection if self._conn is not initialised
        if self._consumer is None:
            raise Exception("Consumer has not been initialised")

        self._log("Listening for messages")
        for message in self._consumer:
            try:
                event = json.loads(message.value.decode('utf-8'))
                self._log(f"Consumed: {event}")
                self._save(event)
                self._log(f"Saved: {event}")
            except Exception as exc:
                self._log(f"Error: {exc}")
                raise exc

    def _save(self, event):
        """Save stock data event to the Postgres database."""
        event = tuple([self.symbol] + event)
        cursor = self._conn.cursor()
        insert_query = (
            "INSERT INTO stock_data " +
            "(symbol, timestamp, open, high, low, close, adj_close, volume) " +
            "VALUES " + str(event)
        )
        cursor.execute(insert_query)
        self._conn.commit()
        cursor.close()
    
    def _log(self, text):
        """Print a message."""
        print(f"({self.symbol}) {text}")

    @staticmethod
    def _connect_db(config):
        """Create the Postgres database connection."""
        conn = psycopg2.connect(
            host=config["DB_HOST"],
            port=config["DB_PORT"],
            dbname=config["DB_NAME"],
            user=config["DB_USER"],
            password=config["DB_PASSWORD"],
        )
        return conn

def read_data(config, symbol):
    """Runs a Kafka consumer for the given stock symbol."""
    topic = f"stock_data_{symbol.lower()}"
    with Consumer(config=config, topic=topic, symbol=symbol) as consumer:
        consumer.run()

def main(config):
    """
        Runs a Kafka consumer for each stock symbol.
        Each consumer is run concurrently in a separate thread.

        Args:
            config (dict): Config dictionary, must contain the
                folling values:
                > SYMBOLS (list): List of stock symbols
                > DB_HOST (str): Postgres host
                > DB_PORT (int): Postgres port
                > DB_NAME (str): Postgres table name
                > DB_USER (str): Postgres user
                > DB_PASSWORD (str): Postgres password
                > KAFKA_SERV_ADDR (str): Kafka server address
                > KAFKA_GROUP_ID (str): Kaffka group ID

        Returns:
            None

        Raises:
            Exception: Raised with any unexpected error.
    """
    symbols = [symbol.upper() for symbol in config["SYMBOLS"]]
    print(f"Running Kafka consumers for stock symbols {symbols}")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(read_data, config, symbol): symbol for symbol in symbols}
        for future in concurrent.futures.as_completed(futures):
            future.result()

if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description="""
        A Kafka consumer which subscribes to topics 
        to receive real-time stock data events 
        to save into a PostgreSQL Database.
    """)
    parser.add_argument(
        'symbols',
        metavar='symbols',
        type=str,
        nargs='+',
        help='stock symbols to consume messages for',
    )
    args = parser.parse_args()

    # Get .env config
    config = dotenv_values(".env")
    config["SYMBOLS"] = args.symbols

    # Run main function
    main(config)