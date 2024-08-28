from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
#secret key to encrypt cookies
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)


#Table for database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

#Table for Habits
class Habit(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)



@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

#habit 
@app.route("/habit")
def habit():
    habit_list = Habit.query.all()
    return render_template("habit.html", habit_list=habit_list)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    new_habit = Habit(title=title, complete=False)
    db.session.add(new_habit)
    db.session.commit()
    return redirect(url_for("habit"))

@app.route("/update/<int:habit_id>")
def update(habit_id):
    habit = Habit.query.filter_by(id=habit_id).first()
    habit.complete = not habit.complete
    db.session.commit()
    return redirect(url_for("habit"))

@app.route("/delete/<int:habit_id>")
def delete(habit_id):
    habit = Habit.query.filter_by(id=habit_id).first()
    db.session.delete(habit)
    db.session.commit()
    return redirect(url_for("habit"))

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
    with app.app_context():
        db.create_all()
    app.run(debug=True) #to remove before deploying