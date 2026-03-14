from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import UserMixin, login_required, login_user, logout_user

from models import User

auth = Blueprint("auth", __name__)


class AuthUser(UserMixin):
    def __init__(self, user):
        self.user = user

    def get_id(self):
        return str(self.user["_id"])


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        flash("Email and password are required.")
        return render_template("register.html"), 400

    if len(password) < 8:
        flash("Password must be at least 8 characters.")
        return render_template("register.html"), 400

    if User.get_by_email(email):
        flash("An account with that email already exists.")
        return render_template("register.html"), 409

    User.create_user(email, password)
    flash("Account created. You can now sign in.")
    return redirect(url_for("auth.login"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        flash("Email and password are required.")
        return render_template("login.html"), 400

    user = User.get_by_email(email)
    if not user or not User.check_password(user, password):
        flash("Invalid email or password.")
        return render_template("login.html"), 401

    login_user(AuthUser(user))
    return redirect(url_for("index"))


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been signed out.")
    return redirect(url_for("auth.login"))
