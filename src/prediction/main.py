import argparse
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
import yfinance as yf

from keras.layers import Dense, LSTM
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler


def main(symbol):
    """Predict the closing stock price for the given stock symbol."""

    # Load 10 years worth of daily stock data
    df = yf.download(tickers=symbol, period="10y", interval="1d")
    data = df.filter(['Close'])
    dataset = data.values

    # Define training variables 
    batch_size = 60
    training_data_len = math.ceil(len(dataset) * 0.8)

    # Normalise data
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(dataset)

    # Get training data
    x_train, y_train = get_training_data(
        scaled_data,
        batch_size, 
        training_data_len
    )

    # Get test data
    x_test = get_test_data(
        scaled_data,
        batch_size,
        training_data_len
    )

    # Train the model
    model = build_model(batch_size)
    model.fit(x_train, y_train, batch_size=1, epochs=1)

    # Make predictions
    predictions = model.predict(x_test)
    predictions = scaler.inverse_transform(predictions)

    # Plot data against predictions
    plot(symbol, data, predictions, training_data_len)

def get_training_data(scaled_data, batch_size, training_data_len):
    training_data = scaled_data[0:training_data_len, :]
    x_train, y_train = [], []
    for i in range(batch_size, len(training_data)):
        x_train.append(training_data[i-batch_size:i, 0])
        y_train.append(training_data[i, 0])
    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    return x_train, y_train

def get_test_data(scaled_data, batch_size, training_data_len):
    test_data = scaled_data[training_data_len - batch_size: , :]
    x_test = [] 
    for i in range(batch_size, len(test_data)):
        x_test.append(test_data[i-batch_size:i, 0])
    x_test = np.array(x_test)
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    return x_test

def build_model(batch_size):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(batch_size, 1)))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def plot(symbol, data, predictions, training_data_len):
    train = data[:training_data_len]
    valid = data[training_data_len:]
    valid.loc[:, ('Predictions')] = predictions
    
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(16,8))
    plt.title(f'Stock Price Prediction ({symbol.upper()})')
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Close Price USD ($)', fontsize=18)
    plt.plot(train['Close'])
    plt.plot(valid[['Close', 'Predictions']])
    plt.legend(['Train', 'Actual', 'AI Predictions'], loc='lower right')
    plt.show()

if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description="""
        Predict the closing stock price using 
        Artifical Intelligence, by using a recurrent 
        neural network Long Short Term Memory (LSTM).
    """)
    parser.add_argument(
        'symbol',
        metavar='symbol',
        type=str,
        nargs=1,
        help='stock symbol to predict stock price for',
    )
    args = parser.parse_args()
    main(args.symbol[0])