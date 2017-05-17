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

class ResetRules(FlaskForm):
    reset_entry_rules = SubmitField('reset_all',id = 'reset_entry_rules')
  
class RuleForm(FlaskForm):
    logic  = StringField('logic',render_kw={'placeholder': 'AND','size':6,'value':'AND'},default = 'AND')
    condID = StringField('1500',render_kw={'placeholder': '1500','size':6},validators=[Required()])
    flip   = StringField('flip',render_kw={'placeholder': '0','size':2,'value':0},default = '0')
    gap    = StringField('gap',render_kw={'placeholder': '0','size':3,'value':0},default = '0')
    offset = StringField('offset',render_kw={'placeholder': '0','size':7,'value':0},default = '0')
    lowthrs = StringField('lowthrs',render_kw={'placeholder': '0.0','size':8,'value':0},default = '0')
    highthrs = StringField('highthrs',render_kw={'placeholder': '0.0','size':8,'value':0},default = '0')
    para1  = StringField('para1',render_kw={'placeholder': '0.0','size':6,'value':0},default = '0')
    para2  = StringField('para2',render_kw={'placeholder': '0.0','size':6,'value':0},default = '0')
    para3  = StringField('para3',render_kw={'placeholder': '0.0','size':6,'value':0},default = '0')
    para4  = StringField('para4',render_kw={'placeholder': '0.0','size':6,'value':0},default = '0')
    para5  = StringField('para5',render_kw={'placeholder': '0.0','size':6,'value':0},default = '0')
    add_rule  = SubmitField('add_rule',id = 'submit_test_form')
    
class JsBindBubmit(FlaskForm):
    content = StringField('content')
    submit_js = SubmitField('submit_js')