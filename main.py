import requests
import matplotlib.pyplot as plt 
import pandas as pd 
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Access the API key using the environment variable name
API_KEY = os.getenv("apiKey")

app = Flask(__name__)

def get_stock_data(symbol, interval="1min", outputsize="compact"):
    if interval == "1day":
        interval = "daily"  # Adjusted to fetch daily interval data for historical data

    if outputsize == "full":
        outputsize = "full"  # Adjusted to get full historical data

    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_{interval.upper()}&symbol={symbol}&outputsize={outputsize}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data


def generate_graphs(data):
    # Extract historical stock data from the response
    time_series_key = "Time Series (Daily)" if "Time Series (Daily)" in data else "Time Series (1min)"
    stock_data = data[time_series_key]

    # Convert data to a Pandas DataFrame for easier manipulation
    df = pd.DataFrame(stock_data).transpose()
    df.index = pd.to_datetime(df.index)

    # If the interval is "1day," calculate the average daily value (OHLC) to plot a single data point per day
    if "Time Series (1min)" in data:
        df = df.resample("D").mean()

    # Generate the graph
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['4. close'], label="Close Price")
    plt.xlabel("Date")
    plt.ylabel("Stock Price")
    plt.title("Stock Price Trends")
    plt.legend()
    plt.grid()

    # Save the plot to a temporary file
    # You can also return the plot as a base64-encoded image to directly render it in the HTML template
    plt.savefig('static/graph.png')
    plt.close()

    return 'graph.png'  # Return the file name of the generated graph


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        symbol = request.form['symbol']
        interval = request.form['interval']
        outputsize = "compact"

        stock_data = get_stock_data(symbol, interval, outputsize)
        graph_data = generate_graphs(stock_data)

        return render_template('index.html', graph_data=graph_data)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
