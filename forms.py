from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SourceForm(FlaskForm):
    title = StringField("Title: ", validators=[DataRequired()], render_kw={"placeholder": "Title"})
    url = StringField("URL: ", validators=[DataRequired()], render_kw={"placeholder": "URL"})
    submit = SubmitField("Save")

class UserForm(FlaskForm):
    name = StringField('Name: ', validators=[DataRequired()], render_kw={'placeholder': 'Name'})
    password = StringField('Password: ', validators=[DataRequired()], render_kw={'placeholder': 'Password'})
    submit = SubmitField('Submit')