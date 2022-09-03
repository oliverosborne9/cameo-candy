from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import EqualTo, InputRequired, Length, ValidationError


def contains_digit(form, field):
    digit_true = any(char.isdigit() for char in field.data)
    if not digit_true:
        raise ValidationError("Must contain at least 1 digit")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=80)])
    submit = SubmitField()


class RegisterForm(LoginForm):
    confirm_password = PasswordField(
        validators=[
            InputRequired(),
            Length(min=4, max=80),
            EqualTo("password", message="Passwords do not match"),
            contains_digit,
        ]
    )
