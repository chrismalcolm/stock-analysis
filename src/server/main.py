import argparse
import threading
import time
import psycopg2
import waitress

from dataclasses import dataclass
from datetime import datetime
from dotenv import dotenv_values
from flask import Flask, jsonify, request
from flask_json import as_json


DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
AGGREGATES = {
    'symbol': 'symbol',
    'timestamp': 'MIN(timestamp)',
    'open': 'MIN(first_open)',
    'high': 'MAX(high)',
    'low': 'MIN(low)',
    'close': 'MIN(last_close)',
    'adj_close': 'AVG(adj_close)',
    'volume': 'SUM(volume)',
}

@dataclass
class Params:
    """Request query parameters"""
    symbols: list
    metrics: list
    start: str
    end: str

class InvalidParams(Exception):
    pass

class Server(threading.Thread):
    """Class for the API server."""

    APP = 'API_SERVER'

    def __init__(self, config):
        self.host = config["API_HOST"]
        self.port = config["API_PORT"]
        self._conn = self._connect_db(config)
        self._app = self._configure_app()
        self._server = self._configure_server()
        super().__init__(target=self._server.run)

    def shutdown(self):
        """Graceful shutdown of the DB connection and server."""
        if self.is_alive:
            self._conn.close()
            self._server.close()
        self.join(timeout=2)

    def _configure_app(self):
        """Setup the app."""

        app = Flask(self.APP)
        app.config['JSON_ADD_STATUS'] = False

        @app.route('/data', methods=['GET'])
        def get_data():
            """Get the stock data from the DB."""

            # Get query params
            symbols_str = request.args.get('symbols', "")
            if symbols_str == "":
                symbols = []
            else:
                symbols = symbols_str.split(",")
            metrics_str = request.args.get('metrics', "")
            if metrics_str == "":
                metrics = []
            else:
                metrics = metrics_str.split(",")
            start = request.args.get('start', "")
            end = request.args.get('end', "")
            params = Params(
                symbols=symbols,
                metrics=metrics,
                start=start,
                end=end,
            )

            # Handle request
            return self._handle_data(params)


        @app.route('/data', methods=["POST"])
        @as_json
        def post_data():
            """Get the aggregated stock data from the DB."""
            
            # Return an error if no body is present
            if request.json is None:
                return jsonify({'error': "No JSON body in request"}), 400

            # Get body params
            params = Params(
                symbols=request.json.get('symbols', []),
                metrics=request.json.get('metrics', []),
                start=request.json.get('start', ""),
                end=request.json.get('end', ""),
            )

            # Handle request
            return self._handle_data(params)

        return app

    def _handle_data(self, params):
        try:
            # Validate request params
            self._validate_params(params)
        except InvalidParams as exc:
            # Return a 400 if request params are invalid
            return jsonify({'error': str(exc)}), 400

        try:
            # Construct the DB query
            query = self._build_query(params)

            # Initialise DB cursor
            cursor = self._conn.cursor()

            # Select all data from the table
            cursor.execute(query)
            rows = cursor.fetchall()
            resp = self._build_resp(params, rows)

            # Close the DB cursor
            cursor.close()

            # Return a successful response
            return jsonify(resp)

        except Exception as exc:
            # Return a 500 if any errors occur
            return jsonify({'error': str(exc)}), 500

    def _configure_server(self):
        """Setup the server."""
        return waitress.create_server(
            self._app,
            host=self.host, 
            port=self.port,
        )

    @staticmethod
    def _validate_params(params):
        
        date_format = DATE_FORMAT
        valid_metrics = AGGREGATES.keys()

        # Validate symbols
        if params.symbols is None:
            raise InvalidParams("symbols is missing")
        if not isinstance(params.symbols, list):
            raise InvalidParams("symbols is not a list")
        for symbol in params.symbols:
            if type(symbol) != str:
                raise InvalidParams(f"non-string symbol {symbol} detected")
        if "" in params.symbols:
            raise InvalidParams("empty symbol detected")

        # Validate metrics
        if params.metrics is None:
            raise InvalidParams("metrics is missing")
        if not isinstance(params.metrics, list):
            raise InvalidParams("metrics is not a list")
        for metric in params.metrics:
            if type(metric) != str:
                raise InvalidParams(f"non-string metric {metric} detected")
        invalid = list(set(params.metrics) - valid_metrics)
        if len(invalid) != 0:
            raise InvalidParams(f"invalid metrics detected {invalid}")

        # Validate start time
        if params.start is None:
            raise InvalidParams("start is missing")
        if not isinstance(params.start, str):
            raise InvalidParams("start is not a string")
        try:
            datetime.strptime(params.start, date_format)
        except ValueError:
            raise InvalidParams(f"invlaid start time '{params.start}', must use format {date_format}")

        # Validate end time
        if params.end is None:
            raise InvalidParams("end is missing")
        if not isinstance(params.end, str):
            raise InvalidParams("end is not a string")
        try:
            datetime.strptime(params.end, date_format)
        except ValueError:
            raise InvalidParams(f"invlaid end time '{params.end}', must use format {date_format}")
    
    def _build_query(self, params):
        if 'timestamp' in params.metrics:
            return self._build_timestamp_query(params)
        return self._build_aggregate_query(params)

    @staticmethod
    def _build_timestamp_query(params):

        date_format = DATE_FORMAT
        valid_metrics = AGGREGATES.keys()

        # Get timestamp conditions
        start_unix = datetime.strptime(params.start, date_format).timestamp()
        end_unix = datetime.strptime(params.end, date_format).timestamp()
        conditions = [
            f'timestamp >= {start_unix}',
            f'timestamp < {end_unix}',
        ]

        # Get symbol conditions
        if len(params.symbols) != 0:
            symbols_str = ", ".join([f"'{symbol.upper()}'" for symbol in params.symbols])
            conditions.append(f"symbol IN ({symbols_str})")
        
        # Get columns and where clause
        if len(params.metrics) == 0:
            params.metrics = list(valid_metrics)
        columns = ", ".join(sorted(params.metrics))
        clause = " AND ".join(conditions)

        query = f"SELECT {columns} FROM stock_data WHERE {clause} ORDER BY timestamp"
        if 'symbol' in params.metrics:
            query += ", symbol"
        return query

    @staticmethod
    def _build_aggregate_query(params):
        
        date_format = DATE_FORMAT
        aggregates = AGGREGATES

        # Get timestamp conditions
        start_unix = datetime.strptime(params.start, date_format).timestamp()
        end_unix = datetime.strptime(params.end, date_format).timestamp()
        conditions = [
            f'timestamp >= {start_unix}',
            f'timestamp < {end_unix}',
        ]

        # Get symbol conditions
        if len(params.symbols) != 0:
            symbols_str = ", ".join([f"'{symbol.upper()}'" for symbol in params.symbols])
            conditions.append(f"symbol IN ({symbols_str})")
        
        # Get columns, where clause and group by
        if len(params.metrics) == 0:
            params.metrics = list(aggregates.keys())
        columns = ", ".join(aggregates[metric] for metric in sorted(params.metrics) )
        clause = " AND ".join(conditions)
    
        inner_query = f"""(
            SELECT *, 
            FIRST_VALUE(open) OVER w as first_open, 
            LAST_VALUE(close) OVER w as last_close 
        FROM stock_data
            WHERE {clause}
        WINDOW w as (
            PARTITION BY symbol
            ORDER BY timestamp
            RANGE BETWEEN 
                UNBOUNDED PRECEDING AND 
                UNBOUNDED FOLLOWING
            ) 
        )
        """

        query = f"SELECT {columns} FROM {inner_query} as data"
        if 'symbol' in params.metrics:
            query += " GROUP BY symbol"
        return query
        
    @staticmethod
    def _build_resp(params, rows):
        if len(params.metrics) == 0:
            params.metrics = list(AGGREGATES.keys())
        data = []
        for row in rows:
            data_point = {}
            for i, metric in enumerate(sorted(params.metrics)):
                data_point[metric] = row[i]
            data.append(data_point)
        return data

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

def main(config):
    """
        Runs API server.

        Args:
            config (dict): Config dictionary, must contain the
                folling values:
                > API_HOST (str): Hostname for the API server
                > API_PORT (str): Port for the API server
                > DB_HOST (str): Postgres host
                > DB_PORT (int): Postgres port
                > DB_NAME (str): Postgres table name
                > DB_USER (str): Postgres user
                > DB_PASSWORD (str): Postgres password

        Returns:
            None

        Raises:
            Exception: Raised with any unexpected error.
    """
    server = Server(config)
    host = config["API_HOST"]
    port = config["API_PORT"]
    print(f"Starting the server {host}:{port}")
    server.start()
    flag = False
    while not flag:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down server.")
            flag = True
            server.shutdown()

if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description="""
        A Flash HTTP server to handle requests for stock data 
        which can be used for analysis or front-end client visuals.
    """)
    parser.add_argument('-H', '--host',
                        help='host ip',
                        default='localhost')
    parser.add_argument('-p', '--port',
                        help='port of the API server',
                        default='5000')
    args = parser.parse_args()

    # Get .env config
    config = dotenv_values(".env")
    config["API_HOST"] = args.host
    config["API_PORT"] = args.port

    # Run main function
    main(config)