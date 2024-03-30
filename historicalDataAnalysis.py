from flask import Flask, render_template, request
import requests
import plotly.graph_objs as go

app = Flask(__name__)

API_KEY = 'YOUR_API_KEY'
API_URL = 'https://www.alphavantage.co/query'

def fetch_historical_data(base_currency, target_currency):
    params = {
        'function': 'FX_DAILY',
        'apikey': API_KEY,
        'from_symbol': base_currency,
        'to_symbol': target_currency,
        'outputsize': 'compact'  # Adjust as needed
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    dates = list(data['Time Series FX (Daily)'].keys())
    exchange_rates = [float(data['Time Series FX (Daily)'][date]['4. close']) for date in dates]
    return dates, exchange_rates

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/historical_data', methods=['POST'])
def historical_data():
    base_currency = request.form['base_currency']
    target_currency = request.form['target_currency']
    dates, exchange_rates = fetch_historical_data(base_currency, target_currency)
    
    # Create plotly chart
    trace = go.Scatter(x=dates, y=exchange_rates, mode='lines', name=f'{base_currency}/{target_currency}')
    layout = go.Layout(title=f'Historical Exchange Rates: {base_currency}/{target_currency}',
                       xaxis=dict(title='Date'),
                       yaxis=dict(title='Exchange Rate'))
    fig = go.Figure(data=[trace], layout=layout)
    chart = fig.to_html(full_html=False)
    
    return render_template('historical_data.html', chart=chart)

if __name__ == "__main__":
    app.run(debug=True)
