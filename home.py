from flask import Flask, render_template
app = Flask(__name__)

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/pet")
def pet():
    return render_template("pet.html")

