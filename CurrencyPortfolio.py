from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Define database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    portfolios = db.relationship('Portfolio', backref='user', lazy=True)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transactions = db.relationship('Transaction', backref='portfolio', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency_pair = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'buy' or 'sell'
    date = db.Column(db.DateTime, nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)

# Routes for portfolio management
@app.route('/create_portfolio', methods=['GET', 'POST'])
@login_required
def create_portfolio():
    if request.method == 'POST':
        name = request.form['name']
        portfolio = Portfolio(name=name, user_id=current_user.id)
        db.session.add(portfolio)
        db.session.commit()
        return redirect(url_for('view_portfolios'))
    return render_template('create_portfolio.html')

@app.route('/view_portfolios')
@login_required
def view_portfolios():
    portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
    return render_template('view_portfolios.html', portfolios=portfolios)

# Add more routes for updating, deleting portfolios, managing transactions, etc.

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
