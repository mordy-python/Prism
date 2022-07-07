from datetime import datetime
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
    session,
)
from deta import Deta
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
import os
import random

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "hello")
deta = Deta()
users = deta.Base("users")
rays = deta.Base("rays")


def to_follow():
    all_users = users.fetch().items
    to_follow = random.choices(all_users, k=6)
    unique = []
    [unique.append(x) for x in to_follow if x not in unique]
    return unique
    


def get_rays(owner=None):
    if owner:
        return sorted(rays.fetch({"owner": owner}).items, key=lambda x: x['date_posted'], reverse=True)
    return sorted(rays.fetch().items, key=lambda x: x['date_posted'], reverse=True)

def get_owner_data(id):
    user = users.get(id)
    return {
        'username': user['username'],
        'pfp': user['avatar_url'],
        'id': id,
    }

@app.route("/")
def index():
    if "username" in session:
        return render_template(
            "index.html", to_follow=to_follow(), title="Home", posted=get_rays()
        )
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
                session["id"] = user["key"]
                flash('Logged in successfully')
                return redirect(url_for("index"))
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
        style = request.form["style"]
        username = request.form["username"]
        pass1 = request.form["password1"]
        pass2 = request.form["password2"]
        email_exists = users.fetch({"email": email}).items
        username_exists = users.fetch({"username": username}).items
        if email_exists or username_exists:
            flash("Username or Email is already in use")
            return redirect(url_for("signup"))
        if pass1 != pass2:
            flash("Passwords must match!", "error")
            return redirect(url_for("signup"))
        user = {
            "email": email,
            "username": username,
            "password": generate_password_hash(pass1),
            "avatar_url": f"https://avatars.dicebear.com/api/{style}/{username}.svg",
        }
        inserted_user = users.put(user)
        session["id"] = inserted_user["key"]
        session["username"] = inserted_user["username"]
        session["email"] = inserted_user["email"]
        session["pfp"] = inserted_user["avatar_url"]
        return redirect(url_for("index"))
    return render_template("signup.html")


@app.route("/profile/<userId>")
def profile(userId):
    user = users.get(userId)
    if not user:
        flash("User not found", "red")
        return redirect(url_for("index"))
    return render_template(
        "profile.html",
        **user,
        title=f"{user['username']}",
        to_follow=to_follow(),
        rays=get_rays(userId),
    )


@app.route("/save-post", methods=["POST"])
def save_post():
    content = request.form.get("content")
    ray = {
        "content": content,
        "owner_data": get_owner_data(session['id']),
        "date_posted": str(datetime.utcnow()),
        "likes": 0,
        "replies": [],
    }
    inserted_ray = rays.put(ray)
    return jsonify(inserted_ray)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
