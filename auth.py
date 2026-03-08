from flask import Blueprint, flash, redirect, render_template, request, url_for

from models import User

auth = Blueprint("auth", __name__)


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
    return redirect(url_for("auth.register"))
