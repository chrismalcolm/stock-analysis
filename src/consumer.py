import concurrent.futures
import json
import psycopg2
from kafka import KafkaConsumer

SERV_ADDR = "localhost:29092"
GROUP_ID = "group_id"
SYMBOLS = ["MSFT", "AAPL"]

DB_HOST = "localhost"
DB_PORT = 54321
DB_NAME = "yp"
DB_USER = "user"
DB_PASSWORD = "password"

# Connect to the PostgreSQL database
def connect_db():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

# Kafka consumer to read stock data
class Consumer:

    def __init__(self, serv_addr, group_id, topic, symbol):
        self.serv_addr = serv_addr
        self.group_id = group_id
        self.topic = topic
        self.symbol = symbol
        self._consumer = None
        self._conn = connect_db()

    def __enter__(self):
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
        # Consume messages from Kafka
        self._print("Listening for messages")
        for message in self._consumer:
            try:
                event = json.loads(message.value.decode('utf-8'))
                self._print(f"Consumed: {event}")
                self._save(event)
                self._print(f"Saved: {event}")
            except Exception as exc:
                self._print(f"({self.symbol}) Error: {exc}")
                raise exc
                
    def _save(self, event):
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
        
    def _print(self, text):
        print(f"({self.symbol}) {text}")

# Read data for the given ticker
def read_data(symbol):
    topic = f"stock_data_{symbol.lower()}"
    with Consumer(serv_addr=SERV_ADDR, group_id=GROUP_ID, topic=topic, symbol=symbol) as consumer:
        consumer.run()

def main():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(read_data, sym): sym for sym in SYMBOLS}
        for future in concurrent.futures.as_completed(futures):
            future.result()

if __name__ == "__main__":
    main()