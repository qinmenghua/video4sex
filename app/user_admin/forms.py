#-*- coding=utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, DataRequired
from wtforms import ValidationError


class EditForm(FlaskForm):
    username = StringField('用户名', validators=[Length(0, 64)])
