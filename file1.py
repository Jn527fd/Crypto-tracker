import requests
import time
import matplotlib.pyplot as plt
import pandas as pd
import subprocess
import json

def get_prices(symbols):
    symbol_string = ",".join(symbols)
    base_url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol_string}&vs_currencies=usd"

    response = requests.get(base_url)
    data = response.json()

    prices = {}
    for symbol in symbols:
        if symbol in data:
            price = data[symbol]["usd"]
            prices[symbol] = float(price)

    return prices

def display_prices(symbols):
    previous_prices = {}
    data = []
    
    while True:
        prices = get_prices(symbols)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print('\n')
        print(f"Timestamp: {current_time}")
        
        row = {'Timestamp': current_time}

        for symbol, price in prices.items():
            if symbol in previous_prices:
                previous_price = previous_prices[symbol]
                if price > previous_price:
                    price_change = "+"
                    price_change_symbol = "↑"
                elif price < previous_price:
                    price_change = "-"
                    price_change_symbol = "↓"
                else:
                    price_change = ""
                    price_change_symbol = ""

                
                print(f"{symbol}: ${price} {price_change_symbol} {price_change} {abs(price - previous_price):.2f}")
            else:
                print(f"{symbol}: ${price}")
            previous_prices[symbol] = price
            row[symbol] = price
            
        data.append(row)
        df = pd.DataFrame(data)
        df.to_csv('prices.csv', index=False)
        time.sleep(15)


def take_input():
    inputs = []
    print('Enter your desired cryptocurrency to display or ''x'' to exit')
    while True:
        key = input()
        if key == 'x' or key == 'X':
            break
        inputs.append(key)
    return inputs
 
def get_valid_names(symbols):
    valid_names = []
    invalid_names = []
    prices = get_prices(symbols)

    for symbol in symbols:
        if symbol in prices:
            valid_names.append(symbol)
        else:
            invalid_names.append(symbol)

    return valid_names, invalid_names


def get_valid_symbols():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    data = response.json()

    valid_symbols = [coin["name"] for coin in data]
    return valid_symbols




#-----------------------------------------------------------------------------#
print('Hello!, welcome to my crypto currency tracker')
print()
print('Here are acceptable names for cryptocurrencies to track')
popular_cryptocurrency_names = get_valid_symbols()
names = popular_cryptocurrency_names[:8]
names_string = ', '.join(name.lower() for name in names)
print(names_string)

print()
input_data = take_input()
input_data = [data.strip().lower() for data in input_data]

valid_names, invalid_names = get_valid_names(input_data)
invalid_string = ', '.join(name.lower() for name in invalid_names)
valid_string = ', '.join(name.lower() for name in valid_names)

while len(invalid_names) != 0:
    print()
    print("sorry one or more of the cryptocurrency symbols given is wrong")
    print('invalid names :', invalid_string )
    print('valid names   :', valid_string)
    print()
    
    yes_no = input('would you like to continue with just only the valid names [''yes'' or ''no''] :')
    
    if yes_no == 'no':
        print()
        input_data = take_input()
        valid_names, invalid_names = get_valid_names(input_data)
        invalid_string = ', '.join(name.lower() for name in invalid_names)
        valid_string = ', '.join(name.lower() for name in valid_names)
        
    else:
        invalid_names = []
        input_data = valid_names

print()
display_options = input("Enter '1' to display current prices every 15 seconds or '2' to plot todays stock prices of each cryptocurrency given :")
display_options = display_options.strip()

if display_options == "1":
    symbols = input_data
    display_prices(symbols)
    
elif display_options == "2":
    symbols = input_data 
    input_value = json.dumps(symbols)
    subprocess.run(["python", "file2.py", input_value])    
    
else:
    print("Invalid option. Please try again.")
