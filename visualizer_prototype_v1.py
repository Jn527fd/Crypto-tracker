import requests
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
import sys
import json
import numpy as np

# input_value = sys.argv[1]
# symbols = json.loads(input_value)

symbols = ['bitcoin', 'ethereum', 'litecoin']

high_24h = {}  # Dictionary to store the 24-hour high for each symbol
low_24h = {}  # Dictionary to store the 24-hour low for each symbol
#symbols = ['bitcoin', 'ethereum', 'litecoin', 'lit']
moving_averages = {}

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

def get_high_low(symbol):
    base_url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": 1
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if "prices" in data:
        prices = data["prices"]
        high = max(prices, key=lambda x: x[1])[1]
        low = min(prices, key=lambda x: x[1])[1]

        if symbol not in high_24h or high > high_24h[symbol]:
            high_24h[symbol] = high
        if symbol not in low_24h or low < low_24h[symbol]:
            low_24h[symbol] = low

        return float(high_24h[symbol]), float(low_24h[symbol])
    else:
        print(f"Unable to retrieve 24-hour high and low for symbol '{symbol}'")
        return None, None

fig, axs = plt.subplots(len(symbols), 1, figsize=(8, 6*len(symbols)), squeeze=False)
lines = {}  # Dictionary to store the lines for each symbol
timestamps = {}  # Dictionary to store the timestamps for each symbol
texts = {}  # Dictionary to store the text annotations

def animate(i):
    prices = get_prices(symbols)
    for idx, symbol in enumerate(symbols):
        if symbol not in lines:
            lines[symbol], = axs[idx, 0].plot([], [], linestyle='-', markersize=2)  # Create a line for the symbol

        if not hasattr(animate, 'timestamps'):  # Check if timestamps attribute exists
            animate.timestamps = {}  # Create timestamps attribute if not present
            animate.ys = {}  # Create ys attribute if not present

        if symbol not in animate.timestamps:
            animate.timestamps[symbol] = [datetime.now()]  # Create timestamps for the symbol if not present
            animate.ys[symbol] = [prices[symbol]]  # Create ys for the symbol if not present
        else:
            animate.timestamps[symbol].append(datetime.now())  # Append the new timestamp
            animate.ys[symbol].append(prices[symbol])  # Append the new y value

        timestamps = animate.timestamps[symbol]
        ys = animate.ys[symbol]

        lines[symbol].set_data(timestamps, ys)  # Update the line data
        axs[idx, 0].set_title(symbol)
        axs[idx, 0].set_xlim(min(timestamps), max(timestamps))  # Set x-axis limits based on timestamps

        # Adjust y-axis limits
        y_min = min(ys) - 2
        y_max = max(ys) + 10
        axs[idx, 0].set_ylim(y_min, y_max)
        
        

        # Update text annotations
        if symbol not in texts:
            texts[symbol] = axs[idx, 0].text(0.01, 0.98, '', ha='left', va='top', transform=axs[idx, 0].transAxes)

        current_price = prices[symbol]
        previous_price = ys[-2] if len(ys) >= 2 else current_price
        price_change = current_price - previous_price

        if price_change > 0:
            change_text = f"↑ +{price_change:.2f}"
            color = 'green'
        elif price_change < 0:
            change_text = f"↓ -{abs(price_change):.2f}"
            color = 'red'
        else:
            change_text = "0.00"
            color = 'black'

        high = high_24h.get(symbol, None)
        low = low_24h.get(symbol, None)

        if low is None or low > min(ys):
            low_24h[symbol] = min(ys)
        if high is None or high < max(ys):
            high_24h[symbol] = max(ys)

        if len(ys) >= 1:
            window_size = min(len(ys), 60)
            moving_average = np.mean(ys[-window_size:])
            moving_averages.setdefault(symbol, [[], []])
            moving_averages[symbol][0].append(datetime.now())
            moving_averages[symbol][1].append(moving_average)

            # Fix KeyError by ensuring the key is present in moving_averages
            ma_timestamps = moving_averages.setdefault(symbol, [[], []])[0]
            ma_values = moving_averages.setdefault(symbol, [[], []])[1]
            axs[idx, 0].plot(ma_timestamps, ma_values, '-', color='red', linewidth=1.5)
            moving_average = moving_averages[symbol][1][-1]
        else:
            moving_average = 0

        dev = current_price - moving_average
        texts[symbol].set_text(f"Current price:{current_price:.1f} USD {change_text}\n"
                               f"Moving Avg:{moving_average:.1f} USD\n"
                               f"Price Delta:{dev:.1f} USD\n"
                               f"24hr Low/High:{low_24h[symbol]:.1f} / {high_24h[symbol]:.1f} USD")
        texts[symbol].set_color(color)  # Set text color

fig.tight_layout()  # Adjust subplots layout

if len(symbols) > 1:
    for idx, symbol in enumerate(symbols):
        axs[idx, 0].set_xlabel('Time')
        axs[idx, 0].set_ylabel('Price (USD)')
else:
    axs[0, 0].set_xlabel('Time')
    axs[0, 0].set_ylabel('Price (USD)')

for symbol in symbols:
    high_24h[symbol], low_24h[symbol] = get_high_low(symbol)

ani = animation.FuncAnimation(fig, animate, frames=10, interval=15000)
plt.show()
