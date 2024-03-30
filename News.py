from flask import Flask, render_template
import requests

app = Flask(__name__)

NEWS_API_KEY = 'YOUR_NEWS_API_KEY'
NEWS_API_URL = 'https://newsapi.org/v2/everything'

def get_currency_news():
    params = {
        'apiKey': NEWS_API_KEY,
        'q': 'currency market OR forex OR economic indicators',
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 10  # Adjust as needed
    }
    response = requests.get(NEWS_API_URL, params=params)
    data = response.json()
    articles = data['articles']
    return articles

@app.route('/')
def index():
    currency_news = get_currency_news()
    return render_template('index.html', currency_news=currency_news)

if __name__ == "__main__":
    app.run(debug=True)
