from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading_platform.db'
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
    bio = db.Column(db.Text)
    strategies = db.relationship('Strategy', backref='user', lazy=True)
    trades = db.relationship('Trade', backref='user', lazy=True)
    followed_users = db.relationship('User', secondary='follows',
                                     primaryjoin=(id == 'follows.c.user_id'),
                                     secondaryjoin=(id == 'follows.c.followed_user_id'),
                                     backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

class Strategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency_pair = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'buy' or 'sell'
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Define association table for follows relationship
follows = db.Table('follows',
                   db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                   db.Column('followed_user_id', db.Integer, db.ForeignKey('user.id'))
)

# Routes for user profiles, strategy sharing, trade copying, etc.
# Add routes for authentication, following users, sharing strategies, copying trades, etc.

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
