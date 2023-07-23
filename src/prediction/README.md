# Prediction

## Summary
```
python3 src/prediction/main.py -h

usage: main.py [-h] symbol

Predict the closing stock price using Artifical Intelligence, by using a recurrent neural network Long Short Term Memory (LSTM).

positional arguments:
  symbol      stock symbol to predict stock price for

options:
  -h, --help  show this help message and exit
```

## Screenshots
Running script:
<img width="1792" alt="Screenshot 2023-07-23 at 16 39 07" src="https://github.com/chrismalcolm/stock-analysis/assets/43220741/ed4987fa-97bd-46f1-bac2-5a4f8f17083e">

Output:
<img width="1792" alt="Screenshot 2023-07-23 at 16 39 35" src="https://github.com/chrismalcolm/stock-analysis/assets/43220741/85150594-4e63-4de6-99a7-c7c62ec74667">

## How it works
* It collects the 10 years worth of stock price data from **`Yahoo Finance`** using the yfinance module.

* The **`Training Data`** is compiled using batches of the stock price data from the first 8 years.

* The **`Test Data`** is set as batches from the remaining 2 years.

* The **`Sequential Model`** is complied with two **`LSTM`** layers and two **`Dense`** layers.

* The model is **`Trained`** to fit the training data.

* The models makes **`Predictions`** on the test data.

* A **`Comparision Graph`** for the real stock price vs the predicted is created using the matplotlib module.

* Configure the stock to predict by changing the **`symbol`** argument.
