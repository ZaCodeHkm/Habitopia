from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from pet import hungerFunc, feedFunc, getHunger
import sqlite3
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
#secret key to encrypt cookies
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=80)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")
#check if have same users
    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:   
            raise ValidationError("That username already exists. Please choose a different one.")
        

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=80)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login Successful!", "Success")
            return redirect(url_for("home"))
        else:
            flash("Invalid Username or Password.", "danger")
    return render_template("login.html", form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration Successful! You can now log in.", "success")
            return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/delete_account", methods=['POST'])
@login_required
def delete_account():
    user = current_user

    try:
        db.session.delete(user)
        db.session.commit()
        flash("Your account has been deleted successfully.", "success")
    except Exception as error:
        db.session.rollback()
        flash("An error occurred while deleting your account. Please try again.", "danger")

    logout_user()
    return redirect(url_for('register'))


#habit 
@app.route("/habit")
@login_required
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
    return redirect(url_for("index"))


@app.route("/delete/<int:habit_id>")
def delete(habit_id):
    habit = Habit.query.filter_by(id=habit_id).first()
    db.session.delete(habit)
    db.session.commit()
    return redirect(url_for("habit"))

#-----PET-----#
@app.route("/pet", methods=["GET","POST"])
@login_required
def pet():
    print("hungerFunc is working")
    hungerFunc()
    return render_template("pet.html", satiety=getHunger())

# def usercheck(): #code to check if user is logged in
#     something something authentication verification
# def petsOwned(): #code to check number of pets owned per user
#     conn_obj = sqlite3.connect('database.db', check_same_thread=False)
#     curs_obj = conn_obj.cursor()

@app.route("/petfeed", methods=['POST'])
def pet_feed():
    petHunger = str(getHunger())
    print("Hunger was: "+petHunger)
    feedFunc()
    petHunger = str(getHunger())
    print("Hunger now: "+petHunger)
    return render_template("pet.html", satiety=petHunger)

@app.route("/shop")
@login_required
def shop():
    return render_template("shop.html")

@app.route("/account")
@login_required
def account():
    return render_template("account.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True) #to remove before deploying