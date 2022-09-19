from time import time

from flask import Blueprint, render_template, session
from flask_login import current_user, login_required

from candy.objects.model import Images
from candy.objects.twin import Twin

drawing_blueprint = Blueprint("drawing", __name__)


@drawing_blueprint.route("/draw", methods=["GET"])
@login_required
def draw():
    colours = Twin.from_current_app().colours
    return render_template("draw.html", colours=colours.to_dict())


@drawing_blueprint.route("/progress", methods=["GET"])
def progress():
    tasks: dict = session["tasks"]
    cols = "_".join(tasks.keys())
    colours = Twin.from_current_app().colours
    return render_template(
        "progress.html",
        cols=cols,
        tasks=tasks,
        ts=int(time()),
        colours=colours.to_dict(),
    )


@drawing_blueprint.route("/gallery", methods=["GET"])
@login_required
def gallery():
    images = (
        Images.query.filter_by(user_id=current_user.id)
        .order_by(Images.datetime.desc())
        .all()
    )
    return render_template("gallery.html", images=images)
