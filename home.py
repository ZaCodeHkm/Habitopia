from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo
from pet import hungerFunc, feedFunc, getHunger
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask import jsonify
from collections import defaultdict
from flask_bcrypt import Bcrypt
import sqlite3


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


#Table for User
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class UserItems(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    coins = db.Column(db.Integer, nullable=False, default=0)
    petFood = db.Column(db.Integer, nullable=False, default=0)


#-----Login & Registration-----
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


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "Current Password"})
    new_password = PasswordField(validators=[InputRequired(), Length(min=8, max=80)], render_kw={"placeholder": "New Password"})
    confirm_new_password = PasswordField(validators=[InputRequired(), EqualTo('new_password', message='Passwords must match')], render_kw={"placeholder": "Confirm New Password"})
    submit = SubmitField("Change Password")


#--Table for Pets
class Pets(db.Model):
    def mydefault(context):
        return context.get_current_parameters()['currentTime']
    
    with app.app_context():
        petOwner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        petID = db.Column(db.Integer, primary_key=True)
        petName = db.Column(db.String(30), nullable=False, default='Sereno')
        lastfedTime = db.Column(db.DateTime, default=mydefault)
        currentTime = db.Column(db.DateTime, default=datetime.now)
        hunger = db.Column(db.Integer)
        petType = db.Column(db.Integer, nullable=False, default=1)
        petXP = db.Column(db.Integer)
        petLevel = db.Column(db.Integer, nullable=False)

        def __repr__(self):
            return f"{self.petName}"
        
class PetsOwned(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    petsOwned = db.Column(db.Integer, nullable=False, default=0)
    pet1 = db.Column(db.Integer, nullable=False, default=0)
    pet2 = db.Column(db.Integer, nullable=False, default=0)
    pet3 = db.Column(db.Integer, nullable=False, default=0)
    pet4 = db.Column(db.Integer, nullable=False, default=0)
    pet5 = db.Column(db.Integer, nullable=False, default=0) 


#-----Table for Habits-----
class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20), default="blue")
    tag = db.Column(db.String(50), default="")
    frequency = db.Column(db.Integer, default=30)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    repeat_days = db.Column(db.String(100), default="")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
     

class HabitLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    checked = db.Column(db.Boolean, default=False)


#-----Diary Feature-----
class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    text = db.Column(db.Text, nullable=False)

    user = db.relationship('User', backref='diary_entries', lazy=True)

class PetsOwned(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    petsOwned = db.Column(db.Integer, nullable=False, default=0)
    pet1 = db.Column(db.Integer, nullable=False, default=0)
    pet2 = db.Column(db.Integer, nullable=False, default=0)
    pet3 = db.Column(db.Integer, nullable=False, default=0)
    pet4 = db.Column(db.Integer, nullable=False, default=0)
    pet5 = db.Column(db.Integer, nullable=False, default=0)

class UserItems(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    coins = db.Column(db.Integer, nullable=False, default=60)
    petFood = db.Column(db.Integer, nullable=False, default=5)

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


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "Current Password"})
    new_password = PasswordField(validators=[InputRequired(), Length(min=8, max=80)], render_kw={"placeholder": "New Password"})
    confirm_new_password = PasswordField(validators=[InputRequired(), EqualTo('new_password', message='Passwords must match')], render_kw={"placeholder": "Confirm New Password"})
    submit = SubmitField("Change Password")





@app.route("/")
def home():
    username = None
    if current_user.is_authenticated:
        username = current_user.username
    return render_template("home.html", username=username)

###############Account System Stuff #####################
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

            user_items = UserItems(user_id=new_user.id, coins=60, petFood=3) # Set coins & petfood to 0
            db.session.add(user_items)
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

@app.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        #check if current password matches the one in database
        if bcrypt.check_password_hash(current_user.password, form.current_password.data):
            # Check if the new password is the same as the old password
            if bcrypt.check_password_hash(current_user.password, form.new_password.data):
                flash("Your new password cannot be the same as the old password.", "danger")
                # Return early, stopping the rest of the function from executing
                return render_template("change_password.html", form=form)
               
            hashed_new_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password = hashed_new_password
            
            try:
                db.session.commit()
                flash("Your password has been changed successfully!", "success")
                return redirect(url_for('account'))
            except Exception as error:
                db.session.rollback()
                flash("An error occurred while updating your password. Please try again.", "danger")
        else:
            flash("Your current password is incorrect.", "danger")
    
    return render_template("change_password.html", form=form)

#-----------  habit  ---------- # 
@app.route("/habit")
@login_required
def habit():
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    selected_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    month_start = datetime.strptime(selected_month, '%Y-%m').date()
    month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
    habit_logs = HabitLog.query.filter(HabitLog.habit_id.in_([habit.id for habit in habits]),
                                       HabitLog.date.between(month_start, month_end)).all()
    habit_logs_dict = {(log.habit_id, log.date.strftime('%Y-%m-%d')): log for log in habit_logs}


    return render_template('habit.html', habits=habits, selected_month=selected_month, month_start=month_start, 
                           month_end=month_end, habit_logs=habit_logs_dict, datetime=datetime, timedelta=timedelta, 
                           relativedelta=relativedelta)


@app.route('/add_habit', methods=['POST'])
def add_habit():
    name = request.form['name']
    tag = request.form['tag']
    frequency = int(request.form['frequency'])
    repeat_days = ','.join(request.form.getlist('repeat_days'))
    new_habit = Habit(name=name, tag=tag, frequency=frequency, repeat_days=repeat_days, user_id=current_user.id)
    
    db.session.add(new_habit)
    flash("Habit Succesfully Added!", "success")
    db.session.commit()
    return redirect(url_for('habit'))

@app.route('/complete_habit/<int:habit_id>', methods=['POST'])
def complete_habit(habit_id):
    today = datetime.now().date()
    log = HabitLog.query.filter_by(habit_id=habit_id, date=today).first()
    
    if not log:
        new_log = HabitLog(habit_id=habit_id, date=today, checked=True)
        db.session.add(new_log)
        flash("Habit completed!", "success")
    
        user_items = UserItems.query.filter_by(user_id=current_user.id).first()
        if user_items:
            user_items.coins += 10  # Add 10 coins
        else:
            user_items = UserItems(user_id=current_user.id, coins=10, petFood=0)
            flash("You've earned 10 coins!", "coin_reward")
            db.session.add(user_items)
        db.session.commit()    
    return redirect(url_for('habit'))




@app.route("/delete/<int:habit_id>", methods=['POST'])
def delete(habit_id):
    habit = Habit.query.filter_by(id=habit_id).first()
    db.session.delete(habit)
    flash("Habit Succesfully Deleted", "failed")
    db.session.commit()   
    return redirect(url_for("habit"))

@app.route("/notifications", methods=["GET"])
@login_required
def get_notifications():
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    today_weekday = datetime.now().strftime('%A')  # Get current weekday
    notifications = []

    for habit in habits:
        if habit.repeat_days:
            repeat_days = habit.repeat_days.split(',')
            if today_weekday in repeat_days:
                notifications.append(f"Reminder for your habit: {habit.name} (Repeat on {today_weekday})")

    return jsonify(notifications=notifications)

#Diary
@app.route('/add_diary', methods=['POST'])
@login_required
def add_diary():
    date = request.form['date']
    text = request.form['text']
    new_entry = DiaryEntry(date=datetime.strptime(date, '%Y-%m-%d').date(), text=text, user_id=current_user.id)
    db.session.add(new_entry)
    db.session.commit()
    return redirect(url_for('habit'))


@app.route('/diary_entries', methods=['GET'])
def diary_entries():
    entries = DiaryEntry.query.filter_by(user_id=current_user.id).all()
    return render_template('habit.html', diary_entries=entries)

@app.route('/delete_diary/<int:entry_id>', methods=['POST'])
def delete_diary(entry_id):
    entry = DiaryEntry.query.get(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('habit'))


#-----Pets-----#
@app.route("/pet", methods=["GET","POST"])
@login_required
def pet():
    # usercheck = db.session.query(PetsOwned).with_entities(PetsOwned.user_id).filter(PetsOwned.user_id==current_user.id).first()
    usercheck = PetsOwned.query.filter_by(user_id = current_user.id).first()
    print(usercheck)
    # print(current_user.id)
    if (usercheck == None):#if user is new and has no pets, this value will be None.
        #here is that gives the user their pet and sends the pets name to DB       
        return render_template("firstpetcreate.html")
    if (usercheck.petsOwned >= 1):
        petname = Pets.query.filter_by(petOwner = current_user.id).first()
        return render_template("pet.html", petname=petname)

@app.route("/firstpetcreate", methods=["GET","POST"])
@login_required
def firstpetCreate():
    if request.method == "POST":
        firstPet()
    return render_template("firstpetcreate.html")

def firstPet():
    petname = request.form['petname']
    newPet = Pets(petOwner=current_user.id, petName=petname, hunger=100, petXP=0, petLevel=1)
    countPet = PetsOwned(user_id=current_user.id, petsOwned = 1, pet1 = 1)
    db.session.add(newPet)
    db.session.add(countPet)
    db.session.commit()
    # print(petname)
    # new_pet = Pets(petName=f'{petname}', petType=1, petLevel=1, petOwner=current_user)
    # current_user.petsOwned = 1
    # db.session.add(new_pet)
    # db.session.commit()
    return render_template("firstpetcreate.html")
    
# @app.route("/generalpetcreate", methods=["GET","POST"])
# def generalPet():
#     petname = request.form['petname']
#     if petBuyType = 2: #subject to change depending on shop
#         newPet = Pets(petOwner=current_user.id, petName=petname, hunger=100,petType=2, petXP=0, petLevel=1)
#     if petBuyType = 3: #subject to change depending on shop
#         newPet = Pets(petOwner=current_user.id, petName=petname, hunger=100,petType=3, petXP=0, petLevel=1)
#     if petBuyType = 4: #subject to change depending on shop
#         newPet = Pets(petOwner=current_user.id, petName=petname, hunger=100,petType=4, petXP=0, petLevel=1)
#     if petBuyType = 5: #subject to change depending on shop
#         newPet = Pets(petOwner=current_user.id, petName=petname, hunger=100,petType=5, petXP=0, petLevel=1)

@app.route("/returnpet", methods=["GET", "`POST"])
def returnpet():
    return redirect(url_for("pet"))

# @app.route("/namepet", methods=["POST"])
# def returnpet():
#     #add function to name pets
#     return render_template("pet.html")

# def firstPet():
#     # usercheck = User.query.get(1)
#     print('free pet given')
#     current_user.petsOwned = 1
#     db.session.commit()
#     print(current_user.petsOwned) #testline
# # def petsOwned(): #code to check number of pets owned per user
# #     conn_obj = sqlite3.connect('database.db', check_same_thread=False)
# #     curs_obj = conn_obj.cursor()

# @app.route("/petfeed", methods=['POST'])
# def pet_feed():
#     petHunger = str(getHunger())
#     print("Hunger was: "+petHunger)
#     feedFunc()
#     petHunger = str(getHunger())
#     print("Hunger now: "+petHunger)
#     return render_template("pet.html", satiety=petHunger)

#--------------------------------------shop----------------------------------------------------#
@app.route("/shop")
@login_required
def shop():
    user_items = UserItems.query.filter_by(user_id=current_user.id).first()
    return render_template("shop.html", coins=user_items.coins, petFood=user_items.petFood)

#@app.route("/buy_item", methods=['POST'])
#@login_required
#def buy_item():
    #items = request.form.get('item')
    #price = int(request.form.get('price'))

    #user_items = UserItems.query.filter_by(user_id=current_user.id).first()

    #if user_items.coins >= price:
    #    user_items.coins -= price

    #    if items == 'pet_food':
    #        user_items.petfood +=1

#-----Account-----#
@app.route("/account")
@login_required
def account():
    return render_template("account.html", user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

#-----Runs the app-----#
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True) #to remove before deploying