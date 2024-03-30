from flask import Flask, render_template, request
import speech_recognition as sr
import requests

app = Flask(__name__)

API_KEY = 'YOUR_API_KEY'
API_URL = 'https://www.alphavantage.co/query'

def convert_currency(from_currency, to_currency, amount):
    params = {
        'function': 'CURRENCY_EXCHANGE_RATE',
        'from_currency': from_currency,
        'to_currency': to_currency,
        'apikey': API_KEY
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    exchange_rate = float(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])
    converted_amount = amount * exchange_rate
    return converted_amount

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        return text
    except Exception as e:
        print("Error:", str(e))
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voice_command', methods=['POST'])
def voice_command():
    try:
        command = speech_to_text()
        if command:
            command = command.lower()
            if 'convert' in command:
                parts = command.split(' ')
                from_currency = parts[parts.index('from') + 1]
                to_currency = parts[parts.index('to') + 1]
                amount_index = parts.index('convert') + 1
                amount = float(parts[amount_index])
                converted_amount = convert_currency(from_currency, to_currency, amount)
                return f"Converted amount: {converted_amount:.2f} {to_currency.upper()}"
            else:
                return "Command not recognized."
        else:
            return "Could not recognize speech."
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
