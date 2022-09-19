from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import EqualTo, InputRequired, Length, ValidationError


def contains_digit(_, field: PasswordField):
    """
    Validator callback function
    to check the password entered contains a digit.
    """
    digit_true = any(char.isdigit() for char in field.data)
    if not digit_true:
        raise ValidationError("Must contain at least 1 digit")


class LoginForm(FlaskForm):
    """
    Form requiring user to input Username and Password, with a submit button
    """

    username = StringField(validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=80)])
    submit = SubmitField()


class RegisterForm(LoginForm):
    """
    Form for user signup, extending LoginForm
    by adding additional confirm password field.
    """

    confirm_password = PasswordField(
        validators=[
            InputRequired(),
            Length(min=4, max=80),
            EqualTo("password", message="Passwords do not match"),
            contains_digit,
        ]
    )


class FormFormatting:
    """
    Object to help format the Login form
    and serve assistive messages to the user.
    Attributes are parsed to the auth.html Jinja template,
    for both the login and register routes.

    :param register: Whether the instance is for
        a registration form, prompting
    """

    def __init__(self, register: bool = False):
        self.register = register
        self.heading = "Sign Up" if register else "Sign In"
        self.password_placeholder = "New Password" if register else "Your Password"
