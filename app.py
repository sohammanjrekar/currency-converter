from flask import Flask, render_template, request
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score
import xgboost as xgb
import lightgbm as lgb
import requests
import datetime

app = Flask(__name__)

# -----------------------------
# API key & cache
# -----------------------------
API_KEY = os.environ.get('EXCHANGE_API_KEY', '11c4b241233ee93ba4f5f3b9')
CACHE_DIR = 'fx_cache'
os.makedirs(CACHE_DIR, exist_ok=True)

# -----------------------------
# Fetch FX historical data (cached CSVs)
# -----------------------------
def fetch_historical_data(from_c, to_c):
    # Placeholder: use your existing CSV fetching logic
    raise NotImplementedError("Historical data fetching requires your cached CSVs")

def get_cache_file(from_c, to_c):
    return os.path.join(CACHE_DIR, f"{from_c}_{to_c}.csv")

def is_cache_stale(file_path, hours=24):
    if not os.path.exists(file_path):
        return True
    file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    return (datetime.datetime.now() - file_time).total_seconds() > hours*3600

def get_historical_data_cached(from_c, to_c):
    file_path = get_cache_file(from_c, to_c)
    if is_cache_stale(file_path):
        df = fetch_historical_data(from_c, to_c)  # Replace with API/proc logic if needed
        df.to_csv(file_path, index=False)
    else:
        df = pd.read_csv(file_path)
        if 'index' in df.columns:
            df.index = pd.to_datetime(df['index'])
    return df

# -----------------------------
# Live currency conversion using ExchangeRate-API pair endpoint
# -----------------------------
def convert_currency_pair(from_c, to_c, amount):
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_c}/{to_c}/{amount}"
    response = requests.get(url).json()
    if response.get("result") != "success":
        raise ValueError(f"API error: {response}")
    conversion_result = response.get("conversion_result")
    return conversion_result, response

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            from_c = request.form['from_c']
            to_c = request.form['to_c']

            conversion_result, response = convert_currency_pair(from_c, to_c, amount)

            from_c_name = response.get('base_code', from_c)
            to_c_name = response.get('target_code', to_c)
            time = response.get('time_last_update_utc', '')

            return render_template('index.html', result=round(conversion_result, 4), amount=amount,
                                   from_c_name=from_c_name, to_c_name=to_c_name, time=time)
        except Exception as e:
            return f'<h1>Bad Request: {e}</h1>'
    return render_template('index.html')

# -----------------------------
# Prediction route (historical CSVs, voting ensemble)
# -----------------------------
@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    from_c = request.args.get('from_c', 'EUR')
    to_c = request.args.get('to_c', 'USD')

    try:
        df = get_historical_data_cached(from_c, to_c)
        df['return'] = df['close'].pct_change()
        df['ma_3'] = df['close'].rolling(3).mean()
        df['ma_7'] = df['close'].rolling(7).mean()
        df.dropna(inplace=True)

        X = df[['ma_3', 'ma_7', 'return']]
        y = df['close'].shift(-1).dropna()
        X = X.iloc[:-1, :]

        # Voting ensemble
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        xgb_model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
        lgb_model = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
        ensemble = VotingRegressor(estimators=[('rf', rf_model), ('xgb', xgb_model), ('lgb', lgb_model)])
        ensemble.fit(X, y)

        next_pred = ensemble.predict([X.iloc[-1]])[0]
        last_close = df['close'].iloc[-1]
        pred_return = np.clip((next_pred / last_close) - 1, -1, 1)

        recommendation = (f"Consider a BUY order for {to_c} (expected rise {pred_return*100:.2f}%)"
                          if pred_return > 0 else
                          f"Consider a SELL order for {to_c} (expected drop {abs(pred_return)*100:.2f}%)")

        result = f"{from_c}/{to_c} predicted change: {abs(pred_return)*100:.2f}% ({'UP' if pred_return>0 else 'DOWN'})"

        # Directional metrics
        N = 5
        if len(X) > N:
            y_true = (y[-N:] > df['close'].iloc[-N-1:-1].values).astype(int)
            y_pred = (ensemble.predict(X[-N:]) > df['close'].iloc[-N-1:-1].values).astype(int)
            accuracy = accuracy_score(y_true, y_pred)*100
            precision = precision_score(y_true, y_pred, zero_division=0)*100
            recall = recall_score(y_true, y_pred, zero_division=0)*100
        else:
            accuracy = precision = recall = None

        return render_template('prediction.html', result=result, recommendation=recommendation,
                               accuracy=accuracy, precision=precision, recall=recall)

    except Exception as e:
        return f"<h1>Error: {e}</h1>"

if __name__ == "__main__":
    app.run(debug=True)
