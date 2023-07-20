from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

# Database connection configuration
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

# Endpoint to get data from the table
@app.route('/data', methods=['GET'])
def get_data():
    tickers = request.args.get('tickers').split(",")
    start = request.args.get('start')
    end = request.args.get('end')

    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Select all data from the table
        select_query = "SELECT * FROM stock_data"
        cursor.execute(select_query)
        rows = cursor.fetchall()

        # Format the data as a list of dictionaries
        data = []
        for row in rows:
            data.append({
                'symbol': row[0],
                'unix': row[1],
                'open': row[2],
                'high': row[3],
                'low': row[4],
                'close': row[5],
                'adj_close': row[6],
                'volume': row[7],
            })

        cursor.close()
        conn.close()

        return jsonify(data)

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500

if __name__ == '__main__':
    app.run(debug=True)