# Stonks

### Description
**Stonks** is a simple command-line stock market checker.

It basically fetches stock market data using **Yahoo Finance**, and displays your favorite tickers informations in the command prompt.

You can also set the amount of shares you own for any ticker, and Stonks will calculate your **daily profit and loss** (P&L).

![alt text](https://github.com/alessio26gas/stonks/blob/main/images/Screenshot.png?raw=true)

### Usage
Stonks uses a configuration file named `.stonks.cfg` in order to work. If the file does not exist, Stonks will automatically create it.

You can edit the config file at any time, just save the file and **restart Stonks to apply your changes**.

![alt text](https://github.com/alessio26gas/stonks/blob/main/images/config.png?raw=true)

Inside the config file you are also allowed to edit the **minimum refresh delay between updates**, and also the **preferred currency** that you want to use in P&L and Balance calculations.

By setting `enable-debug-mode` to `True`, the software will show the **Debug Mode** section:

![alt text](https://github.com/alessio26gas/stonks/blob/main/images/Screenshot_debug.png?raw=true)

You can easily exit the program at any time using `Ctrl+C`.

### Files Description
The main python script is located in `stonks/stonks.py`

An example config is located in `stonks/.stonks.cfg`
