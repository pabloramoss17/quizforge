from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from model.userdto import UserDto
from db import srp 

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        usr = UserDto.find(srp, email)

        if usr and usr.chk_password(password):
            login_user(usr)
            return redirect(url_for("index"))
        else:
            flash("Correo o contraseña incorrectos")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Las contraseñas no coinciden")
            return redirect(url_for("auth.register"))
        
        if UserDto.find(srp, email) is None:
            usr = UserDto(email, password)
            srp.save(usr)
            login_user(usr)
            flash("Usuario registrado exitosamente. Ahora puedes iniciar sesión.")
            return redirect(url_for("index"))
        else:
            flash("El correo electrónico ya está registrado")

    return render_template("register.html")

