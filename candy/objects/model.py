import os

from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

db = SQLAlchemy()
login_manager = LoginManager()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(120))


class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    datetime = db.Column(db.DateTime)
    img_loc = db.Column(db.String(80))


def image_cleanup(mapper, connection, target: Images):
    """
    Callback function to delete an image file
    after its row is removed from the Images table
    in the database.
    """
    os.unlink(target.img_loc)


event.listen(Images, "after_delete", image_cleanup)
