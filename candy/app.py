import random
import string
from os import getenv

from distutils.util import strtobool
from flask import Flask, render_template
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap5
from flask_login import current_user

from candy.objects import DATABASE_CONNECTION_URI
from candy.objects.model import Images, User, db, login_manager
from candy.objects.twin import Twin
from candy.routes.drawing import drawing_blueprint
from candy.routes.general import general_blueprint
from candy.routes.helper import helper_blueprint


def page_not_found(e):
    return render_template("404.html"), 404


def create_app() -> Flask:

    app = Flask(__name__)

    twin = Twin.from_local()
    twin.log()

    app.config.update(
        SQLALCHEMY_DATABASE_URI=DATABASE_CONNECTION_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        BOOTSTRAP_SERVE_LOCAL=strtobool(getenv("SERVE_LOCAL", "False")),
        TWIN=twin,
    )
    Bootstrap5(app)

    db.init_app(app)
    app.app_context().push()
    db.create_all()

    app.secret_key = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=20)
    )

    app.register_blueprint(general_blueprint)
    app.register_blueprint(drawing_blueprint)
    app.register_blueprint(helper_blueprint)

    app.register_error_handler(404, page_not_found)

    login_manager.init_app(app)
    login_manager.login_view = "general.login"

    class CustomModelView(ModelView):
        def is_accessible(self):
            return current_user.is_authenticated

    admin = Admin(app, template_mode="bootstrap4")
    admin.add_view(CustomModelView(User, db.session))
    admin.add_view(CustomModelView(Images, db.session))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def user():
        user = False if current_user.is_anonymous else current_user.username
        return dict(user=user)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=6040)  # nosec:B104
