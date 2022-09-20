import json
import shutil
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from uuid import uuid4

import requests
from flask import Blueprint, flash, request, session
from flask_login import current_user
from loguru import logger

from candy.objects.image import Drawing
from candy.objects.model import Images, db
from candy.objects.twin import Twin

helper_blueprint = Blueprint("helper", __name__)


@helper_blueprint.route("/submit", methods=["POST"])
def submit():
    twin = Twin.from_current_app()
    dispense_url = twin.hardware_api.url

    image = Drawing.from_post_request(request.values["imageBase64"])
    image.save("latest.png")
    quantities = json.loads(request.values["quantities"])

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
                f"{dispense_url}/async",
                data={"colour": colour, "quantity": quantity},
            )
            if r.status_code == HTTPStatus.FAILED_DEPENDENCY:
                flash(f"ERROR: {r.text}", category="danger")
                return "Scales Offline", 304
            task_id = r.json().get("task_id")
            tasks[colour] = task_id
    session["tasks"] = tasks
    return "OK", HTTPStatus.ACCEPTED


@helper_blueprint.route("/task/<task_id>", methods=["GET"])
def task(task_id):
    dispense_url = Twin.from_current_app().hardware_api.url

    r = requests.get(f"{dispense_url}/status/{task_id}")
    body = r.json()
    progress_pct = int(100 * body["current"] / body["total"])
    return str(progress_pct), HTTPStatus.ACCEPTED
