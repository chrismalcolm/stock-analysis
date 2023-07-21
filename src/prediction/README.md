# Prediction

## Summary
Predict the closing stock price using Artifical Inteligence, by using a recurrent neural network Long Short Term Memory (LSTM).

## Demo
insert video here

## How it works
* It collects the 10 years worth of stock price data from **`Yahoo Finance`** using the yfinance module.

* The **`Training Data`** is compiled using batches of the stock price data from the first 8 years.

* The **`Test Data`** is set as batches from the remaining 2 years.

* The **`Sequential Model`** is complied with two **`LSTM`** layers and two **`Dense`** layers.

* The model is **`Trained`** to fit the training data.

* The models makes **`Predictions`** on the test data.

* A **`Comparision Graph`** for the real stock price vs the predicted is created using the matplotlib module.

* A ticker can be configured by changing the **`SYMBOL`** in the script.