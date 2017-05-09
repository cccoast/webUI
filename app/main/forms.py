from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,IntegerField
from wtforms.validators import Required
from flask_wtf.file import FileField,FileAllowed,FileRequired
from .. import ufile

class UploadForm(FlaskForm):
    upload_file = FileField(validators=[
        FileAllowed(ufile, 'IMG allowed'), 
        FileRequired('not selected')])
    submit = SubmitField('upload')
    
class TestForm(FlaskForm):
    start_spot = IntegerField('start_spot',id = 'start_spot',validators=[],
                           render_kw={'placeholder': 0},default = 0)
    end_spot   = IntegerField('end_spot', id = 'end_spot',validators=[],
                           render_kw={'placeholder': 32000},default = 32000)
    spot_step  = IntegerField('spot_step', id = 'spot_step',validators=[],
                           render_kw={'placeholder': 1},default = 1)
    submit1  = SubmitField('upload')