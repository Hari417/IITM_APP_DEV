from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp


EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class RegistrationForm(FlaskForm):
    full_name = StringField(
        "Full name",
        validators=[DataRequired(), Length(max=100)]
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Length(max=120),
            Regexp(EMAIL_PATTERN, message="Enter a valid email address.")
        ]
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, max=128)]
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match.")
        ]
    )
    role = SelectField(
        "Register as",
        choices=[("student", "Student"), ("examiner", "Examiner")],
        validators=[DataRequired()]
    )
    registration_number = StringField(
        "Registration number",
        validators=[Length(max=50)]
    )
    department = StringField(
        "Department",
        validators=[DataRequired(), Length(max=100)]
    )
    programme = StringField(
        "Programme",
        validators=[Length(max=100)]
    )
    phone = StringField(
        "Phone",
        validators=[Length(max=20)]
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Length(max=120)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
