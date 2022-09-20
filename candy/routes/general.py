from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from loguru import logger
from werkzeug.security import check_password_hash, generate_password_hash

from candy.objects.forms import FormFormatting, LoginForm, RegisterForm
from candy.objects.model import User, db
from candy.objects.twin import Twin

general_blueprint = Blueprint("general", __name__)

INDEX = "general.index"


@general_blueprint.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and check_password_hash(user.password, login_form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for(INDEX))
        flash("Invalid username or password", "error")
    return render_template(
        "auth.html", form=login_form, form_formatting=FormFormatting(register=False)
    )


@general_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for(INDEX))


@general_blueprint.route("/register", methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        username = register_form.username.data.lower()
        user = User.query.filter_by(username=username).first()
        if user:
            flash("User already exists.", "danger")
            return redirect(url_for("general.register"))
        hashed_password = generate_password_hash(
            register_form.password.data, method="sha256"
        )
        logger.info(len(hashed_password))
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("User created successfully... Welcome!", category="success")
        return redirect(url_for(INDEX))
    return render_template(
        "auth.html", form=register_form, form_formatting=FormFormatting(register=True)
    )


@general_blueprint.route("/", methods=["GET"])
def index():
    text = Twin.from_current_app().welcome_text
    return render_template("index.html", text=text)
