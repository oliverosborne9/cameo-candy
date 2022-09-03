import json
import shutil
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from time import time
from uuid import uuid4

import requests
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from loguru import logger
from werkzeug.security import check_password_hash, generate_password_hash

from candy.objects.forms import LoginForm, RegisterForm
from candy.objects.image import Drawing
from candy.objects.model import Images, User, db
from candy.objects.twin import Twin

blueprint = Blueprint("routes", __name__)

INDEX = "routes.index"


class FormFormatting:
    def __init__(self, register: bool = False):
        self.register = register
        self.heading = "Sign Up" if register else "Sign In"
        self.password_placeholder = "New Password" if register else "Your Password"


@blueprint.route("/login", methods=["GET", "POST"])
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


@blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for(INDEX))


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        username = register_form.username.data.lower()
        user = User.query.filter_by(username=username).first()
        if user:
            flash("User already exists.", "danger")
            return redirect(url_for("routes.register"))
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


@blueprint.route("/", methods=["GET"])
def index():
    twin: Twin = current_app.config["TWIN"]
    return render_template("index.html", text=twin.welcome_text)


@blueprint.route("/draw", methods=["GET"])
@login_required
def draw():
    twin: Twin = current_app.config["TWIN"]
    return render_template("draw.html", colours=twin.colours.to_dict())


@blueprint.route("/submit", methods=["POST"])
def submit():
    image = Drawing.from_post_request(request.values["imageBase64"])
    image.save("latest.png")
    quantities = json.loads(request.values["quantities"])
    logger.info(quantities)

    img_loc = Path(image.save_dir) / str(uuid4())
    img_record = Images(
        user_id=current_user.id, datetime=datetime.utcnow(), img_loc=str(img_loc)
    )
    shutil.copyfile(Path(image.save_dir) / "latest.png", img_loc)
    db.session.add(img_record)
    db.session.commit()

    import time

    # CHECK SCALES PROPERLY
    if int(str(time.time())[-1]) % 2 == 0:
        time.sleep(1)
        return "Scales Offline", 304
    tasks: dict = {}
    for colour, quantity in quantities.items():
        if int(quantity):
            logger.info(quantity, colour)
            r = requests.post(
                "http://mechanic:7070/api/v1/dispense/async",
                data={"colour": colour, "quantity": quantity},
            )
            if r.status_code == HTTPStatus.FAILED_DEPENDENCY:
                flash(f"ERROR: {r.text}", category="danger")
                return "Scales Offline", 304
            task_id = r.json().get("task_id")
            tasks[colour] = task_id
    session["tasks"] = tasks
    return "OK"


@blueprint.route("/progress", methods=["GET"])
def progress():
    tasks: dict = session["tasks"]
    logger.info(tasks)
    cols = "_".join(tasks.keys())
    ts = int(time())
    twin = current_app.config["TWIN"]
    return render_template(
        "progress.html", cols=cols, tasks=tasks, ts=ts, colours=twin.colours.to_dict()
    )


# to do: return dict with full info to be handled on client side
@blueprint.route("/task/<task_id>", methods=["GET"])
def task(task_id):
    r = requests.get(f"http://mechanic:7070/api/v1/dispense/status/{task_id}")
    body = r.json()
    progress_pct = int(100 * body["current"] / body["total"])
    return str(progress_pct), 200


@blueprint.route("/gallery", methods=["GET"])
@login_required
def gallery():
    images = (
        Images.query.filter_by(user_id=current_user.id)
        .order_by(Images.datetime.desc())
        .all()
    )
    return render_template("gallery.html", images=images)
