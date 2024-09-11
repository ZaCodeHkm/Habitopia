from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from pet import hungerFunc, feedFunc, getHunger
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask import jsonify


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
    
    habits = db.relationship('Habit', backref='user', lazy=True)


class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20), default="blue")
    tag = db.Column(db.String(50), default="")
    frequency = db.Column(db.Integer, default=30)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Change backref name to 'habit_logs' to avoid conflict
    logs = db.relationship('HabitLog', backref='habit_logs', cascade="all, delete-orphan")  # Cascade delete


class HabitLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    checked = db.Column(db.Boolean, default=False)

    # Explicit relationship only if needed
    habit = db.relationship('Habit', backref='habit_log', lazy=True)  # Remove conflict here


#Diary Feature
class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    text = db.Column(db.Text, nullable=False)

    user = db.relationship('User', backref='diary_entries', lazy=True)

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
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    selected_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    month_start = datetime.strptime(selected_month, '%Y-%m').date()
    month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
    
    logs = HabitLog.query.filter(
        HabitLog.date.between(month_start, month_end),
        HabitLog.habit_id.in_([habit.id for habit in habits])
    ).all()
    diary_entries = DiaryEntry.query.filter_by(user_id=current_user.id).all()

    return render_template('habit.html', habits=habits, logs=logs, selected_month=selected_month, month_start=month_start, datetime=datetime, timedelta=timedelta, relativedelta=relativedelta, diary_entries=diary_entries)


@app.route('/add_habit', methods=['POST'])
def add_habit():
    name = request.form['name']
    color = request.form['color']
    tag = request.form['tag']
    frequency = int(request.form['frequency'])
    new_habit = Habit(name=name, color=color, tag=tag, frequency=frequency, user_id=current_user.id)
    db.session.add(new_habit)
    db.session.commit()
    return redirect(url_for('habit'))

@app.route('/toggle_check/<int:habit_id>/<string:date>', methods=['POST'])
def toggle_check(habit_id, date):
    try:
        data = request.get_json()
        checked = data.get('checked')
        
        print(f"Received request: habit_id={habit_id}, date={date}, checked={checked}")  # Debug print
        
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        log = HabitLog.query.filter_by(habit_id=habit_id, date=date_obj).first()
        
        if log:
            log.checked = checked
        else:
            new_log = HabitLog(habit_id=habit_id, date=date_obj, checked=checked)
            db.session.add(new_log)

        db.session.commit()
        print("Database updated successfully")  # Debug print
        return jsonify({'success': True, 'checked': checked})

    except Exception as e:
        print(f"Error in toggle_check: {str(e)}")  # Debug print



@app.route("/delete/<int:habit_id>", methods=['POST'])
def delete(habit_id):
    habit = Habit.query.filter_by(id=habit_id).first()
    db.session.delete(habit)
    db.session.commit()
       
    return redirect(url_for("habit"))

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