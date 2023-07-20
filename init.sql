CREATE TABLE stock_data (
    symbol VARCHAR(4) NOT NULL,
    timestamp FLOAT NOT NULL,
    open FLOAT NOT NULL,
    high FLOAT NOT NULL,
    low FLOAT NOT NULL,
    close FLOAT NOT NULL,
    adj_close FLOAT NOT NULL,
    volume FLOAT NOT NULL
);