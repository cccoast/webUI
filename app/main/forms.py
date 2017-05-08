from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_wtf.file import FileField,FileAllowed,FileRequired
from .. import ufile

class UploadForm(FlaskForm):
    upload_file = FileField(validators=[
        FileAllowed(ufile, 'IMG allowed'), 
        FileRequired('not selected')])
    submit = SubmitField('upload')

