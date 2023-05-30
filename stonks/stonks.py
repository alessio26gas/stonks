from math import log, floor
from time import time, sleep
from configparser import ConfigParser
import requests
import concurrent.futures
import os

def main():

    if not os.path.isfile(".stonks.cfg"):
        print("Error: Config file not found\nNew config file '.stonks.cfg' successfully created")
        createconfig()
        os._exit(0)

    config = ConfigParser()
    config.read(".stonks.cfg")

    try:
        symbols = config._sections['Portfolio']
        for symbol in symbols: symbols[symbol] = float(symbols[symbol])
        noshares = all(symbols[symbol] == 0 for symbol in symbols)
        curr = config._sections['Settings']['currency']
        delay = abs(float(config._sections['Settings']['refresh-delay']))
        debug = config._sections['Settings']['enable-debug-mode'] == 'True'

    except Exception as e:
        print("\033[31mAn error regarding config file occurred.\033[0m")
        print(str(e))
        os._exit(0)

    cls()
    print('\033[1mSTONKS\033[0m v1.0.0')
    print('Retrieving data...')

    executor = concurrent.futures.ThreadPoolExecutor(max_workers = len(symbols))
    start = time()

    while 1:
        try:
            debugtime1 = time()

            if curr != 'USD':
                currency = get_stock_data(curr + '=X', 0)
                currency.name = 'USD/' + curr

            debugtime2 = time()

            futures = [executor.submit(get_stock_data, symbol, symbols[symbol]) for symbol in symbols]
            list = [future.result() for future in concurrent.futures.as_completed(futures)]

            debugtime3 = time()

            if delay != 0 and (debugtime1 - start) > 0.1: sleep(delay - (time() - start) % delay)
            cls()
            print('\033[1mSTONKS\033[0m v1.0.0')
            print('\n\033[1mWATCHLIST\033[0m')
            print('Ticker'.ljust(7) + 'Volume'.rjust(8) + 'Price'.rjust(11) + 'Change'.rjust(8) 
                  + (('Shares'.rjust(18) + 'P&L($)'.rjust(10) + (('P&L(€)' if curr == 'EUR' else f"P&L({curr})") if curr != 'USD' else "").rjust(10)) if not noshares else ""))

            list1 = [i for i in list if i.shares != 0]
            list2 = [i for i in list if i.shares == 0]

            list1.sort(key = lambda x: x.percent_change, reverse = True)
            list2.sort(key = lambda x: x.percent_change, reverse = True)

            list = list1 + list2

            profit, total = 0, 0
            for ticker in list:
                profit = profit + ticker.shares * ticker.change
                total = total + ticker.shares * ticker.price
                print(color(ticker.change)
                    + f"{ticker.name}".ljust(7) + f"{ticker.volume}".rjust(8) + ("  ▲ " if ticker.change >= 0 else "  ▼ ")
                    + f"{ticker.price:.2f}".rjust(7) + f"{ticker.change:+.2f}".rjust(8) + f"({ticker.percent_change:+.2f}%)".rjust(10)
                    + ((f"{ticker.shares:g}".rjust(8) + f"{ticker.shares * ticker.change:+.2f}".rjust(10) 
                    + ((f"{ticker.shares * ticker.change * currency.price:+.2f}".rjust(10)) if curr != 'USD' else "")) if ticker.shares != 0 else "")
                    + "\033[0m")
            
            if curr != 'USD':
                print("\n\033[1mCURRENCY CHANGE\033[0m")
                print(color(currency.change) + f"{currency.name}".ljust(10) 
                    + ("▲ " if currency.change>=0 else "▼ ") 
                    + f"{currency.price:.5f}".rjust(7) 
                    + f"{currency.change:+.5f}".rjust(10) 
                    + f"({currency.percent_change:+.2f}%)".rjust(10)+"\033[0m")
                
                if not noshares:
                    print("\n\033[1m"+"BALANCE:".ljust(9)+"\033[0m" 
                        + color(profit) + (((f"€") if curr == 'EUR' else f"{curr} ") + f"{total * currency.price:.2f}").rjust(10)
                        + f"{profit * currency.price:+.2f}".rjust(10)
                        + f"({100 * profit / (total - profit):+.2f}%)".rjust(10) + "\033[0m")
                
            else:
                if not noshares:
                    print("\n\033[1m"+"BALANCE:".ljust(9)+"\033[0m" 
                        + color(profit) + f"${total:.2f}".rjust(10)
                        + f"{profit:+.2f}".rjust(10)
                        + f"({100 * profit / (total - profit):+.2f}%)".rjust(10) + "\033[0m")
            
            print("\n\033[33mPress Ctrl-C to quit\033[0m")

            if debug:
                print("\n\033[36m\033[1mDEBUG MODE\033[0m\033[36m")
                print(f"Currency = {curr}")
                print(f"No Shares Mode = {noshares}")
                print(f"Delay value set: {delay}")
                print(f"Delay 1: {debugtime2 - debugtime1:.3f} s (Parse Currency Data)")
                print(f"Delay 2: {debugtime3 - debugtime2:.3f} s (Parse Tickers Data)")
                print(f"Delay 3: {time() - debugtime1:.3f} s (Whole iteration)\033[0m")
            
        except Exception as e:
            print("\n\033[31mAn error occurred, reloading...\033[0m")
            print(str(e))
            pass

        except KeyboardInterrupt:
            cls()
            os._exit(0)


def get_stock_data(symbol, shares):
    api_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"interval": "1d", "range": "2d"}
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0"}
    api_response = requests.get(api_url, headers=headers, params=params)
    json_response = api_response.json()
    data = json_response["chart"]["result"][0]["indicators"]["quote"][0]
    close = data["close"]
    volume = human_format(data["volume"][-1]) if data["volume"][-1] != 0 else 0
    previous_close = close[-2]
    price = close[-1]
    change = price - previous_close
    percent_change = (change / previous_close) * 100
    return Ticker(symbol.upper(), volume, price, change, percent_change, shares)


def human_format(number):
    units = ['', 'K', 'M', 'B', 'T']
    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return '%.1f%s' % (number / k**magnitude, units[magnitude])


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def color(number):
    if number > 0: return ("\033[32m") 
    elif number == 0: return("\033[33m")
    else: return("\033[31m")


def createconfig():
    config = ConfigParser()
    config["Portfolio"] = {
        "AAPL": 10,
        "GOOG": 10,
        "AMZN": 0,
        "MSFT": 0
    }
    config["Settings"] = {
        "currency": 'USD',
        "refresh-delay": 1.0,
        "enable-debug-mode": False
    }
    with open(".stonks.cfg", "w") as f:
        f.write("## Stonks Config File\n")
        f.write("## Type tickers in your portfolio specifying the number of shares you own (es. 'AAPL=30')\n## or add them to your watchlist using 0 (es. 'AMZN=0')\n")
        config.write(f)


class Ticker:
    def __init__(self, name, volume, price, change, percent_change, shares):
        self.name = name
        self.volume = volume
        self.price = price
        self.change = change
        self.percent_change = percent_change
        self.shares = shares
        
main()
