from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Length, Email

class JoinForm(FlaskForm):
    username = StringField(label='Name', validators=[DataRequired(),Length(min=1,max=20)])
    roomCode = StringField(label='Room Code', validators=[DataRequired(),Length(min=5,max=5)])
    play = SubmitField(label="Play")

class AnswerForm(FlaskForm):
    answer = StringField(label='Answer', validators=[DataRequired(),Length(min=1,max=30)])
    submit = SubmitField(label="Submit")
