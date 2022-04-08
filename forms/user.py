from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat Password', validators=[DataRequired()])
    name = StringField('Username', validators=[DataRequired()])
    surname = StringField('Surname')
    # about = TextAreaField("Немного о себе")
    submit = SubmitField('Sign up')
