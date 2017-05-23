# coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Optional


class CodeForm(FlaskForm):
    code = StringField(u'礼品卡', validators=[DataRequired()])
    submit = SubmitField('兑换')

