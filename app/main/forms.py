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
    
class TestTableForm(FlaskForm):
    start_spot = StringField('start_spot',id = 'test_start_spot',validators = [Required()],
                           render_kw={'placeholder': '0'},
                           default = '0')
    end_spot   = StringField('end_spot', id = 'test_end_spot',validators = [Required()],
                           render_kw={'placeholder': '32000'},
                           default = '32000')
    spot_step  = StringField('spot_step', id = 'test_spot_step',validators = [Required()],
                           render_kw={'placeholder': '1'},
                           default = '1')
    submit1  = SubmitField('upload',id = 'submit_test_form')