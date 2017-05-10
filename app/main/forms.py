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
    logic  = StringField('logic',render_kw={'placeholder': 'AND','size':6},default = 'AND')
    condID = StringField('1500',render_kw={'placeholder': '1500','size':6},default = '1500')
    flip   = StringField('flip',render_kw={'placeholder': '0','size':6},default = '0')
    gap    = StringField('gap',render_kw={'placeholder': '0','size':6},default = '0')
    offset = StringField('offset',render_kw={'placeholder': '0','size':6},default = '0')
    lowthrs = StringField('lowthrs',render_kw={'placeholder': '0.0','size':6},default = '0')
    highthrs = StringField('highthrs',render_kw={'placeholder': '0.0','size':6},default = '0')
    para1  = StringField('para1',render_kw={'placeholder': '0.0','size':6},default = '0')
    para2  = StringField('para2',render_kw={'placeholder': '0.0','size':6},default = '0')
    para3  = StringField('para3',render_kw={'placeholder': '0.0','size':6},default = '0')
    para4  = StringField('para4',render_kw={'placeholder': '0.0','size':6},default = '0')
    para5  = StringField('para5',render_kw={'placeholder': '0.0','size':6},default = '0')
    submit_rule  = SubmitField('submit',id = 'submit_test_form')