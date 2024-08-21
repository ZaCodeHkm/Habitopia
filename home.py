from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)


#Table for database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/habit")
def habit():
    return render_template("habit.html")

@app.route("/pet")
def pet():
    return render_template("pet.html")

@app.route("/shop")
def shop():
    return render_template("shop.html")

@app.route("/account")
def account():
    return render_template("account.html")


if __name__ == "__main__":
    app.run(debug=True) #to remove before deploying