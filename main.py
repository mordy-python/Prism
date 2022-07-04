from flask import Flask, flash, redirect, render_template, request, url_for, session
from deta import Deta
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
import os

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "hello")
deta = Deta()
users = deta.Base("users")


@app.route("/")
def index():
    if "username" in session:
        return render_template("index.html")
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user_exists = users.fetch({"email": email}).items
        if user_exists: 
            user = user_exists[0]
            saved_passw = user["password"]
            if check_password_hash(saved_passw, password):
                session["username"] = user["username"]
                session["email"] = user["email"]
                session["pfp"] = user["avatar_url"]
                return redirect(url_for('index'))
            else:
                flash("Email or password is incorrect", "error")
                return redirect(url_for("login"))
        else:
            flash("Email or password is incorrect", "error")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    if "username" in session:
        session.clear()
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "username" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        pass1 = request.form["password1"]
        pass2 = request.form["password2"]
        email_exists = users.fetch({"email": email}).items
        username_exists = users.fetch({"username": username}).items
        if email_exists or username_exists:
            flash("Username or Email is already in use", "error")
            print("1!")
            return redirect(url_for("signup"))
        if pass1 != pass2:
            flash("Passwords must match!", "error")
            return redirect(url_for("signup"))
        user = {
            "email": email,
            "username": username,
            "password": generate_password_hash(pass1),
            "avatar_url": f"https://avatars.dicebear.com/api/micah/{username}.svg",
        }
        users.insert(user)
        session["username"] = username
        return redirect(url_for("index"))
    return render_template("signup.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
