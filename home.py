from flask import Flask, render_template, url_for, request, redirect, flash, session, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from werkzeug.utils import secure_filename



app = Flask(__name__)
bcrypt = Bcrypt(app)

#database url
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
    coins = db.Column(db.Integer, nullable=False, default=60)
    petFood = db.Column(db.Integer, nullable=False, default=3)
    bait = db.Column(db.Integer, nullable=False, default=1)

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


#-----Table for Habits-----
class Habit(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.Integer, default=30)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    repeat_days = db.Column(db.String(100), default="")
    
     

class HabitLog(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    checked = db.Column(db.Boolean, default=False)


#-----Diary Feature-----
class DiaryEntry(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    text = db.Column(db.Text, nullable=False)

    user = db.relationship('User', backref='diary_entry', lazy=True)

#--Table for Pets
class Pets(db.Model):
    def mydefault(context):
        return context.get_current_parameters()['currentTime']
    
    with app.app_context():
        petOwner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        petID = db.Column(db.Integer, primary_key=True)
        petName = db.Column(db.String(30), nullable=False, default='noname')
        lastfedTime = db.Column(db.Integer, default=mydefault)
        currentTime = db.Column(db.Integer, default=datetime.now().timestamp())
        cumulTime = db.Column(db.Integer, default=0)
        hunger = db.Column(db.Integer, default=100)
        petType = db.Column(db.Integer, nullable=False, default=1)
        petXP = db.Column(db.Integer, default=0)
        petLevel = db.Column(db.Integer, nullable=False, default=1)
        activePet = db.Column(db.Integer, default=0, nullable=False)

        def __repr__(self):
            return f"{self.petName}"

class PetsOwned(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    petsOwned = db.Column(db.Integer, nullable=False, default=0)
    pet1 = db.Column(db.Integer, nullable=False, default=0)
    pet2 = db.Column(db.Integer, nullable=False, default=0)
    pet3 = db.Column(db.Integer, nullable=False, default=0)


#Login and Registration
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

#--------Notification System---------#

class Notification(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(10), nullable=False)  
    time = db.Column(db.String(5), nullable=False)
    type = db.Column(db.String(50), nullable=False)  

    def __init__(self, user_id, text, type):
        self.user_id = user_id
        self.text = text
        self.date = datetime.now().strftime('%Y-%m-%d')
        self.time = datetime.now().strftime('%H:%M')
        self.type = type

#--------Account Page System--------#
class Account(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    bio = db.Column(db.String(500), nullable=True)



###===FLASK ROUTING===###
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

            user_items = UserItems(user_id=new_user.id, coins=60, petFood=3, bait=1) # Set coins, petfood, bait
            db.session.add(user_items)
            db.session.commit()
            
            flash("Registration Successful! You can now log in.", "success")
            return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/delete_account", methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    try:
        
        UserItems.query.filter_by(user_id=user.id).delete()
        Pets.query.filter_by(petOwner=user.id).delete()
        PetsOwned.query.filter_by(user_id=user.id).delete()
        Habit.query.filter_by(user_id=user.id).delete()
        HabitLog.query.filter_by(user_id=user.id).delete()
        DiaryEntry.query.filter_by(user_id=user.id).delete()
        Notification.query.filter_by(user_id=user.id).delete()
        Account.query.filter_by(user_id=user.id).delete()

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
    user_items = UserItems.query.filter_by(user_id=current_user.id).first()
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    selected_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    month_start = datetime.strptime(selected_month, '%Y-%m').date()
    month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
    habit_logs = HabitLog.query.filter(HabitLog.habit_id.in_([habit.id for habit in habits]),
                                       HabitLog.date.between(month_start, month_end)).all()
    habit_logs_dict = {(log.habit_id, log.date.strftime('%Y-%m-%d')): log for log in habit_logs}
    diary_entries = DiaryEntry.query.filter_by(user_id=current_user.id).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).all()

    return render_template('habit.html', habits=habits, selected_month=selected_month, month_start=month_start, 
                            month_end=month_end, habit_logs=habit_logs_dict, datetime=datetime, timedelta=timedelta, 
                            relativedelta=relativedelta, diary_entries=diary_entries, notifications=notifications, user_items=user_items)


@app.route('/add_habit', methods=['POST'])
def add_habit():
    name = request.form['name']
    frequency = int(request.form['frequency'])
    repeat_days = ','.join(request.form.getlist('repeat_days'))
    new_habit = Habit(name=name, frequency=frequency, repeat_days=repeat_days, user_id=current_user.id)
    
    db.session.add(new_habit)
    flash("Habit Succesfully Added!", "success")
    db.session.commit()
    return redirect(url_for('habit'))

@app.route('/complete_habit/<int:habit_id>', methods=['POST'])
def complete_habit(habit_id):
    today = datetime.now().date()
    log = HabitLog.query.filter_by(habit_id=habit_id, date=today).first()
    
    if not log:
        new_log = HabitLog(user_id=current_user.id, habit_id=habit_id, date=today, checked=True)
        db.session.add(new_log)
        flash("Habit completed!", "success")
    
        user_items = UserItems.query.filter_by(user_id=current_user.id).first()
        if user_items:
            user_items.coins += 10 
            flash("You've earned 10 coins!", "coin_reward")
        else:
            user_items = UserItems(user_id=current_user.id, coins=10, petFood=0)
            flash("You've earned 10 coins!", "coin_reward")
            db.session.add(user_items)
        db.session.commit()    
    return redirect(url_for('habit'))




@app.route("/delete/<int:habit_id>", methods=['POST'])
def delete(habit_id):
    habit = Habit.query.filter_by(id=habit_id).first()
    if habit:
        today = datetime.now().date()
        start_of_month = today.replace(day=1)
        count = db.session.query(db.func.count(HabitLog.id)).filter(HabitLog.user_id == current_user.id,
                                                                    HabitLog.date.between(start_of_month, today)).scalar()
        if count < 7:
            if count == 3:
                flash("Slow down! You can only delete 7 habits in a month", "failed")
            db.session.delete(habit)
            log = HabitLog.query.filter_by(habit_id=habit_id).first()
            if log:
                db.session.delete(log)
                flash("Habit Succesfully Deleted", "failed")
            else:
                flash("Habit Succesfully Deleted", "failed")
            db.session.commit()   
            return redirect(url_for("habit"))
        else:
            flash("You can delete only 7 habits in a month", "failed")
            return redirect(url_for("habit"))
    else:
        flash("Habit not found", "failed")
        return redirect(url_for("habit"))


@app.route("/undo_complete/<int:habit_id>", methods=['GET', 'POST'])
def undo_complete(habit_id):
    today = datetime.now().date()
    log = HabitLog.query.filter_by(habit_id=habit_id, date=today).first()
    if log:
        db.session.delete(log)
        flash("Habit Uncompleted", "failed")

        user_items = UserItems.query.filter_by(user_id=current_user.id).first()
        if user_items:
            user_items.coins -= 10  
            flash("You've lost 10 coins", "coin_reward")
        else:
            user_items = UserItems(user_id=current_user.id, coins=-10, petFood=0)
            flash("You've Lost 10 coins", "coin_reward")
            db.session.add(user_items)

    db.session.commit()   
    return redirect(url_for("habit"))


@app.before_request
def get_notifications():
    if current_user.is_authenticated and request.endpoint == 'habit': 
        last_visit = session.get('last_visit')  
        current_date = datetime.now().strftime('%Y-%m-%d') 
        
        if not last_visit or last_visit != current_date:
            session['last_visit'] = current_date  

            habits = Habit.query.filter_by(user_id=current_user.id).all()
            today_weekday = datetime.now().strftime('%A')  

            for habit in habits:
                if habit.repeat_days:
                    repeat_days = habit.repeat_days.split(',')
                    if today_weekday in repeat_days:
                        # Create a notification and save it in the database
                        notification = Notification(
                            user_id=current_user.id,
                            text=f"Reminder for your habit: {habit.name} (Repeat on {today_weekday})",
                            type='reminder'
                        )
                        db.session.add(notification)
            db.session.commit()
    
            return None
def cleanup_old_notifications():
    old_notifications = Notification.query.filter(Notification.date != datetime.now().strftime('%Y-%m-%d')).all()
    for notification in old_notifications:
        db.session.delete(notification)
    db.session.commit()

#Diary


@app.route('/diary', methods=['GET'])
@login_required
def diary():
    entries = DiaryEntry.query.filter_by(user_id=current_user.id).all()
    return render_template('diary.html', diary_entries=entries)

@app.route('/add_diary', methods=['POST'])
@login_required
def add_diary():
    date = datetime.now().date()
    text = request.form['text']
    new_entry = DiaryEntry(date=date, text=text, user_id=current_user.id)
    db.session.add(new_entry)
    db.session.commit()
    return redirect(url_for('diary'))

@app.route('/delete_diary/<int:entry_id>', methods=['POST'])
def delete_diary(entry_id):
    entry = DiaryEntry.query.get(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('diary'))


#-----Pets-----#
@app.route("/pet", methods=["GET","POST"])
@login_required
def pet():  
    checkUser = PetsOwned.query.filter_by(user_id = current_user.id).first() #gets the current user based off their ID number
    if (checkUser == None): # if user is new and has no pets, this object will be a NoneType
        return render_template("firstpetcreate.html") # here is where the user gets their first pet
    selectPet = db.session.execute(db.select(Pets).filter_by(petOwner=current_user.id, activePet = 1)).scalar_one()
    if (checkUser.petsOwned >= 1):
        checkUser = db.session.execute(db.select(UserItems).filter_by(user_id=current_user.id)).scalar_one()
        selectPet = db.session.execute(db.select(Pets).filter_by(petOwner=current_user.id, activePet = 1)).scalar_one()
        if selectPet == None:
            noPet = "No pet selected..."
            petimage = "/static/petimages/Empty.png"
            return render_template("pet.html", petname=noPet, XPcount = 0, petlevel = 0, petimage=petimage)
        else:
            hungerFunc()
            if selectPet.cumulTime > 172800:
                return redirect(url_for("runaway"))
            else:
                typecheck = selectPet.petType
                if typecheck == 1: # Pet 1
                    if selectPet.petLevel >= 1 and selectPet.petLevel < 5:
                        petimage = "/static/petimages/AirEgg.png"
                    if selectPet.petLevel >= 5 and selectPet.petLevel < 10:
                        petimage = "/static/petimages/Sereno.png"
                    if selectPet.petLevel >= 10:
                        petimage = "/static/petimages/BeegBird.png" 
                if typecheck == 2: # Pet 2
                    if selectPet.petLevel >= 1 and selectPet.petLevel < 5:
                        petimage = "/static/petimages/EarthEgg.png"
                    if selectPet.petLevel >= 5 and selectPet.petLevel < 10:
                        petimage = "/static/petimages/Mori.png"
                    if selectPet.petLevel >= 10:
                        petimage = "/static/petimages/BeegRat.png" ###
                if typecheck == 3: # Pet 3
                    if selectPet.petLevel >= 1 and selectPet.petLevel < 5:
                        petimage = "/static/petimages/WaterEgg.png" ###
                    if selectPet.petLevel >= 5 and selectPet.petLevel < 10:
                        petimage = "/static/petimages/Newt.png"
                    if selectPet.petLevel >= 10:
                        petimage = "/static/petimages/BeegFeesh.png" ###    
            return render_template("pet.html", petname=selectPet.petName, XPcount = selectPet.petXP, petlevel = selectPet.petLevel,
                                   petimage=petimage, satiety=selectPet.hunger, food=checkUser.petFood)

@app.route("/petfeed", methods=['GET','POST'])
def pet_feed():
    selectPet = db.session.execute(db.select(Pets).filter_by(petOwner=current_user.id, activePet = 1)).scalar_one()
    selectFood = db.session.execute(db.select(UserItems).filter_by(user_id=current_user.id)).scalar_one()
    if selectFood.petFood >= 1:
        selectFood.petFood -= 1
        selectPet.hunger = 100
        selectPet.cumulTime = 0
        xpFunc()
    if selectFood.petFood == 0:
        flash("You dont have any food left.", "info")
    db.session.commit()
    return redirect(url_for("pet"))

@app.route("/petnest", methods=["GET","POST"])
@login_required
def petnest():     # Pet nest images and names
    petCheck = db.session.execute(db.select(PetsOwned).filter_by(user_id=current_user.id)).scalar()
    nameGet1 = Pets.query.filter_by(petOwner = current_user.id, petType = 1).first()
    nameGet2 = Pets.query.filter_by(petOwner = current_user.id, petType = 2).first()
    nameGet3 = Pets.query.filter_by(petOwner = current_user.id, petType = 3).first()
    selectPet1 = db.session.execute(db.select(Pets).filter_by(petOwner=current_user.id, petType = 1)).scalar()
    selectPet2 = db.session.execute(db.select(Pets).filter_by(petOwner=current_user.id, petType = 2)).scalar()
    selectPet3 = db.session.execute(db.select(Pets).filter_by(petOwner=current_user.id, petType = 3)).scalar()

    if petCheck == None:
        return redirect(url_for("pet"))

    if petCheck.pet1 == 1:
        pet1name = nameGet1.petName
        if selectPet1.petLevel >= 1 and selectPet1.petLevel < 5:
            pet1image = "/static/petimages/AirEgg.png"
        if selectPet1.petLevel >= 5 and selectPet1.petLevel < 10:
            pet1image = "/static/petimages/Sereno.png"
        if selectPet1.petLevel >= 10:
            pet1image = "/static/petimages/BeegBird.png"
    if petCheck.pet1 == 0:
        pet1image = "/static/petimages/Empty.png"
        pet1name = "..."

    if petCheck.pet2 == 1:
        pet2name = nameGet2.petName
        if selectPet2.petLevel >= 1 and selectPet2.petLevel < 5:
            pet2image = "/static/petimages/EarthEgg.png"
            
        if selectPet2.petLevel >= 5 and selectPet2.petLevel < 10:
            pet2image = "/static/petimages/Mori.png"
        if selectPet2.petLevel >= 10:
            pet2image = "/static/petimages/BeegRat.png" ###
    if petCheck.pet2 == 0:
        pet2image = "/static/petimages/Empty.png"
        pet2name = "..."

    if petCheck.pet3 == 1:
        pet3name = nameGet3.petName
        if selectPet3.petLevel >= 1 and selectPet3.petLevel < 5:
            pet3image = "/static/petimages/WaterEgg.png" ###
        if selectPet3.petLevel >= 5 and selectPet3.petLevel < 10:
            pet3image = "/static/petimages/Newt.png" ###
        if selectPet3.petLevel >= 10:
            pet3image = "/static/petimages/BeegFeesh.png" ###
    if petCheck.pet3 == 0 :
        pet3image = "/static/petimages/Empty.png"
        pet3name = "..."

    return render_template("petnest.html", pet1name=pet1name, pet2name=pet2name, pet3name=pet3name,
                           pet1image=pet1image, pet2image=pet2image, pet3image=pet3image)

@app.route("/makeactive", methods=['POST']) 
def makeactive():
    if request.form['makeactive'] == "Sereno": # Pet 1
        activeUpdate = Pets.query.filter_by(petOwner = current_user.id, petType = 1).first()
        activeUpdate.activePet = 1
        db.session.add(activeUpdate)

        activeCheck2 = Pets.query.filter_by(petOwner = current_user.id, petType = 2).first()
        if activeCheck2 == None:
            pass
        else:
            activeCheck2.activePet = 0 # Clears Pet 2 of active status
            timeReset()

        activeCheck3 = Pets.query.filter_by(petOwner = current_user.id, petType = 3).first()
        if activeCheck3 == None:
            pass
        else:
            activeCheck3.activePet = 0 # Clears Pet 3 of active status
            timeReset()

        db.session.commit()     
        return redirect(url_for("petnest"))
    
    if request.form['makeactive'] == "Mori": # Pet 2
        activeUpdate = Pets.query.filter_by(petOwner = current_user.id, petType = 2).first()
        if activeUpdate == None: # If the user doesn't have the pet:
           flash("You don't have this pet...", "info") 
           pass
        else: # If the user has the pet:
            activeCheck1 = Pets.query.filter_by(petOwner = current_user.id, petType = 1).first() # 
            if activeCheck1 == None:
                pass
            else:
                activeCheck1.activePet = 0 # Makes pet 1 non-active. Maybe change variable name to clearPet1
                activeUpdate.activePet = 1 # Makes pet 2 active only if they have the pet. Man, i need better variable names.
                db.session.add(activeUpdate)
                timeReset()

            activeCheck3 = Pets.query.filter_by(petOwner = current_user.id, petType = 3).first()
            if activeCheck3 == None:
                pass
            else:
                activeCheck3.activePet = 0    # Clears Pet 3 of active status
                timeReset()

        db.session.commit()
        return redirect(url_for("petnest"))
    
    if request.form['makeactive'] == "pet3": # Pet 3
        activeUpdate = Pets.query.filter_by(petOwner = current_user.id, petType = 3).first()
        if activeUpdate == None:
            flash("You don't have this pet...", "info")
            pass
        else:
            activeCheck1 = Pets.query.filter_by(petOwner = current_user.id, petType = 1).first()
            if activeCheck1 == None:
                pass
            else:
                activeCheck1.activePet = 0
                activeUpdate.activePet = 1
                db.session.add(activeUpdate)
                timeReset()

            activeCheck2 = Pets.query.filter_by(petOwner = current_user.id, petType = 2).first()
            if activeCheck2 == None:
                pass
            else:
                activeCheck2.activePet = 0
                timeReset()

        db.session.commit()
        return redirect(url_for("petnest"))


@app.route("/timereset", methods=["GET","POST"])
def timeReset(): # This is what prevents non-active pets losing hunger after they are made active after some time.
    try:
        selectPet = db.session.execute(db.select(Pets).filter_by(petOwner=current_user.id, activePet = 1)).scalar_one()
        selectPet.lastfedTime = datetime.now().timestamp()
    except:
        pass
    db.session.commit()

@app.route("/firstpetcreate", methods=["GET","POST"]) #To comment out once done.
@login_required
def firstpetCreate():
    if request.method == "POST":
        firstPet()
    return redirect(url_for("pet"))
    
@app.route("/petnaming", methods=["GET","POST"])
@login_required
def petnaming():
    petName = request.form['nameyourpet']
    petType = session.get("petType", None)

    if request.method == "POST":
        if petType == 2:
            selectPet = Pets.query.filter_by(petOwner=current_user.id, petType=2).first()
            selectPet.petName = petName
            db.session.commit()
            return redirect(url_for('petnest'))
        if petType == 3:
            selectPet = Pets.query.filter_by(petOwner=current_user.id, petType=3).first()
            selectPet.petName = petName
            db.session.commit()
            return redirect(url_for('petnest'))

    return render_template("petnaming.html")

@app.route("/runaway", methods=["GET","POST"])
@login_required
def runaway(): 
    selectPet = db.session.execute(db.select(Pets).filter_by(petOwner=current_user.id, activePet = 1)).scalar_one()
    userItems = db.session.execute(db.select(UserItems).filter_by(user_id=current_user.id)).scalar_one()
    return render_template("runaway.html", petname=selectPet.petName,bait=userItems.bait)

@app.route("/lure", methods=["GET","POST"])
def lure():
    selectPet = db.session.execute(db.select(Pets).filter_by(petOwner=current_user.id, activePet = 1)).scalar_one()
    selectBait = db.session.execute(db.select(UserItems).filter_by(user_id=current_user.id)).scalar_one()
    if selectBait.bait >= 1:
        selectBait.bait -= 1
        selectPet.hunger = 100
        selectPet.cumulTime = 0
    if selectBait.bait == 0:
        flash("You dont have any bait left.", "info")
    db.session.commit()
    return redirect(url_for('pet'))

@app.route("/testpet2", methods=["GET","POST"]) #To comment out once done.
@login_required
def testpet2():
    if request.method == "POST":
        givepet2()
    return redirect(url_for("pet"))

@app.route("/testpet3", methods=["GET","POST"]) #To comment out once done.
@login_required
def testpet3():
    if request.method == "POST":
        givepet3()
    return redirect(url_for("pet"))

@app.route("/testfood", methods =["GET", "POST"]) #To comment out once done.
@login_required
def testfood():
    if request.method == "POST":
        giveFood = db.session.execute(db.select(UserItems).filter_by(user_id=current_user.id)).scalar_one()
        giveFood.petFood += 5
        db.session.commit()
    return redirect(url_for("pet"))

@app.route("/testcoins", methods =["GET", "POST"]) #To comment out once done.
@login_required
def testcoins():
    if request.method == "POST":
        giveFood = db.session.execute(db.select(UserItems).filter_by(user_id=current_user.id)).scalar_one()
        giveFood.coins += 9001
        db.session.commit()
    return redirect(url_for("pet"))

@app.route("/returnpet", methods=["GET", "`POST"])
def returnpet():
    return redirect(url_for("pet"))

#--Pet Functions--#
def firstPet():
    petname = request.form['petname']
    newPet = Pets(petOwner=current_user.id, petName=petname, petXP=0, activePet=1)
    countPet = PetsOwned(user_id=current_user.id, petsOwned = 1, pet1 = 1)
    db.session.add(newPet)
    db.session.add(countPet)
    db.session.commit()
    return render_template("firstpetcreate.html")

def givepet2(): #to comment out once done
    givepet2 = Pets(petOwner=current_user.id,petName="testingpet2", hunger=100, petType=2, petXP=0, petLevel=1)
    morePet = PetsOwned.query.get(current_user.id)
    morePet.petsOwned += 1
    morePet2 = PetsOwned.query.get(current_user.id)
    morePet2.pet2 = 1
    db.session.add(givepet2)
    db.session.add(morePet2)
    db.session.commit()
    return redirect(url_for("pet"))

def givepet3(): #to comment out once done
    givepet3 = Pets(petOwner=current_user.id,petName="testingpet3", hunger=100, petType=3, petXP=0, petLevel=1)
    morePet = PetsOwned.query.get(current_user.id)
    morePet.petsOwned += 1
    morePet3 = PetsOwned.query.get(current_user.id)
    morePet3.pet3 = 1
    db.session.add(givepet3)
    db.session.add(morePet3)
    db.session.commit()
    return redirect(url_for("pet"))

def hungerFunc(): # Reduces the active pets hunger. Runs when "Pets" page is loaded (given the user has a pet)
    selectPet = db.session.execute(db.select(Pets).filter_by(petOwner=current_user.id, activePet = 1)).scalar_one()
    selectPet.lastfedTime = selectPet.currentTime
    selectPet.currentTime = datetime.now().timestamp()
    Diff = selectPet.currentTime - selectPet.lastfedTime
    selectPet.cumulTime += Diff
    petName = selectPet.petName
    print(selectPet.cumulTime)
    if selectPet.cumulTime >= 14400 and selectPet.cumulTime < 28800: # 4 hours to 8 hours
        selectPet.hunger = 67
    if selectPet.cumulTime >= 28800 and selectPet.cumulTime < 57600: # 8 hours to 16 hours
        selectPet.hunger = 34
        flash(f"Hey it looks like { petName } is getting hungry!")
    if selectPet.cumulTime >= 57600 and selectPet.cumulTime < 86400: # 16 hours to 24 hours
        selectPet.hunger = 1
    if selectPet.cumulTime > 86400: # 24 hours
        selectPet.hunger = 0
        flash(f"{ petName } is really hungry!")
    db.session.commit()
    if selectPet.cumulTime > 172800: # 48 hours
        petName = selectPet.petName
        return redirect(url_for("runaway"))
    
def xpFunc(): # Runs when pet is fed.
    selectPet = db.session.execute(db.select(Pets).filter_by(petOwner=current_user.id, activePet = 1)).scalar_one()
    selectPet.petXP += 10
    if selectPet.petXP >= 100:
        lvlupFunc()
        selectPet.petXP = 0
    db.session.commit()

def lvlupFunc(): # Runs when xpFunc is run.
    selectPet = db.session.execute(db.select(Pets).filter_by(petOwner=current_user.id, activePet = 1)).scalar_one()
    selectPet.petLevel += 1
    db.session.commit()


#----Shop----#
@app.route("/shop", methods=["GET", "POST"])
@login_required
def shop():

    user_items = UserItems.query.filter_by(user_id=current_user.id).first()
    user_pets = PetsOwned.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        item = request.form['item']

        if item == "pet_food":
            if user_items.coins >= 20:  # Check if user has enough coins
                user_items.coins -= 20  # Deduct 20 coins
                user_items.petFood += 1  # Add 1 pet food to the inventory
                flash("You bought 1 pet food!", "success")
            else:
                flash("Not enough coins to buy pet food.", "danger")

        elif item == "bait":
            if user_items.coins >= 100:
                user_items.coins -= 100  
                user_items.bait += 1 
                flash("You bought 1 bait!", "success")
            else:
                flash("Not enough coins to buy bait.", "danger")

        elif item == "earth_egg":
            if user_pets.pet2 == 0:
                if user_items.coins >= 1000:
                    user_items.coins -= 1000
                    user_pets.petsOwned += 1
                    user_pets.pet2 = 1
                    add_pet2 = Pets(petOwner=current_user.id, hunger=100, petType=2, petXP=0, petLevel=1)
                    db.session.add(add_pet2)
                    db.session.commit()
                    session["petType"] = 2
                    flash("You bought an Earth Egg!", "success")
                    return render_template("petnaming.html", petimage="/static/petimages/EarthEgg.png")
                else:
                    flash("Not enough coins to buy an Earth Egg.", "danger")
            else:
                flash("You already own an Earth Egg.", "danger")

        elif item == "water_egg":
            if user_pets.pet3 == 0:
                if user_items.coins >= 2000:
                    user_items.coins -= 2000
                    user_pets.petsOwned += 1
                    user_pets.pet3 = 1
                    add_pet3 = Pets(petOwner=current_user.id, hunger=100, petType=3, petXP=0, petLevel=1)
                    db.session.add(add_pet3)
                    db.session.commit()
                    session["petType"] = 3
                    flash("You bought a Water Egg!", "success")
                    return render_template("petnaming.html", petimage="/static/petimages/WaterEgg.png")
                else:
                    flash("Not enough coins to buy a Water Egg.", "danger")
            else:
                flash("You already own a Water Egg.", "danger")

        db.session.commit()

    return render_template("shop.html", coins=user_items.coins, petFood=user_items.petFood, bait=user_items.bait)

    

#-----Account-----#
@app.route("/account/")
@login_required
def account():
    user = current_user
    pets_owned = PetsOwned.query.filter_by(user_id=current_user.id).first()
    profile = Account.query.filter_by(user_id=current_user.id).first()
    account = Account.query.filter_by(user_id=current_user.id).first()
    user_items = UserItems.query.filter_by(user_id=current_user.id).first()
    return render_template("account.html", user=user, pets_owned=pets_owned, profile = profile, account = account, user_items = user_items)
@app.route("/edit_account", methods=["GET", "POST"])
@login_required
def edit_account():
    profile = Account.query.filter_by(user_id=current_user.id).first()
    
    img = request.files.get("img")
    bio = request.form.get("bio")

    if profile is None:
        if img and bio:
            filename = secure_filename(img.filename)
            mimetype = img.mimetype
            profile = Account(img=img.read(), bio=bio, user_id=current_user.id, name=filename, mimetype=mimetype)
            db.session.add(profile)
            db.session.commit()
            flash("Your profile has been created!", "success")
        else:
            flash("You must provide both a profile picture and a bio.", "danger")
    else:
        if img:
            filename = secure_filename(img.filename)
            profile.img = img.read()
            profile.name = filename
            profile.mimetype = img.mimetype
        if bio:
            profile.bio = bio
        db.session.commit()
        flash("Your profile has been updated!", "success")

    return redirect(url_for("account"))


@app.route("/account/<int:id>")
def get_img(id):
    img = Account.query.filter_by(id=id).first()
    if img:
        return Response(img.img, mimetype=img.mimetype)
    else:
        return "Image Not Found", 404

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


#Stack Overflow References (that I remember):
# https://stackoverflow.com/questions/6699360/flask-sqlalchemy-update-a-rows-information
# https://stackoverflow.com/questions/43811779/use-many-submit-buttons-in-the-same-form Q: How to get multiple buttons without filtering by method?

#Non SO References
# https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/