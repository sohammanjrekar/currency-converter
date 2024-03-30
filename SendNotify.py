from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
import requests

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@example.com'
mail = Mail(app)

# API URL and API Key
API_URL = 'https://www.alphavantage.co/query'
API_KEY = 'YOUR_API_KEY'

# Placeholder for user preferences (can be replaced with database)
user_preferences = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_preference', methods=['POST'])
def set_preference():
    currency_pair = request.form['currency_pair']
    preferred_rate = float(request.form['preferred_rate'])
    email = request.form['email']
    
    # Store user preference
    user_preferences[(currency_pair, email)] = preferred_rate
    
    return redirect(url_for('index'))

@app.route('/check_alerts')
def check_alerts():
    for (currency_pair, email), preferred_rate in user_preferences.items():
        # Fetch latest exchange rate
        params = {
            'function': 'CURRENCY_EXCHANGE_RATE',
            'apikey': API_KEY,
            'from_currency': currency_pair.split('_')[0],
            'to_currency': currency_pair.split('_')[1]
        }
        response = requests.get(API_URL, params=params)
        data = response.json()
        exchange_rate = float(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])
        
        # Check if exchange rate meets or exceeds preferred rate
        if exchange_rate >= preferred_rate:
            send_email_alert(email, currency_pair, exchange_rate, preferred_rate)
            # Implement push notification here
        
    return 'Alerts checked'

def send_email_alert(email, currency_pair, exchange_rate, preferred_rate):
    subject = f'Exchange rate alert for {currency_pair}'
    body = f'The current exchange rate ({currency_pair}) is {exchange_rate}, which meets or exceeds your preferred rate of {preferred_rate}.'
    msg = Message(subject, recipients=[email], body=body)
    mail.send(msg)

if __name__ == "__main__":
    app.run(debug=True)
