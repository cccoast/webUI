from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, RadioField, SelectMultipleField, IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User
from .. import ufile
from distutils.text_file import TextFile
from openpyxl.drawing.text import TextField

basic_indicators = ['LastPrice','Volume','BidPrice','BidVolume','AskPrice','AskVolume','OpenInterest']

class LoginForm(FlaskForm):
    
    username = StringField('UserName', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required(), Length(1, 64)])
#     remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

'''Create shm''' 

class DataForm(FlaskForm):
    
    start_date = IntegerField('start_date',id = 'start_date',validators=[Required()],
                           render_kw={'placeholder': '20140101'},default = 20140101)
    
    end_date   = IntegerField('end_date', id = 'end_date',validators=[Required()],
                           render_kw={'placeholder': '20141231'},default = 20141231)
    
    level      = RadioField('level',  id = 'level',validators=[Required()],
                            choices = [('tick','tick'),],
                            default = 'tick'
                            )
    
    adjust     = RadioField('adjust', id = 'adjust',validators=[Required()],
                            choices = [#('yes','yes'),
                                        ('no','no')],
                            default = 'no')
    
    indicators = StringField('indicators',id = 'indicators',validators = [],
                             render_kw={'readOnly': "true",\
                                        'placeholder':','.join(basic_indicators),\
                                        'value':','.join(basic_indicators)},
                            )
    
    instruments = SelectMultipleField('instruments', id = 'instruments',
                            choices = [('if0001','if0001'),
                                       ('if0002','if0002'),],
                            default = ['if0001','if0002']
                            )
    
    #or_upload_file = FileField(validators=[FileAllowed(ufile, 'TXT allowed'),])
    submit2     =  SubmitField('generate',id='submit_data')
    
class ModifyDataForm(FlaskForm):
    
    submit3 = SubmitField('ModifyData',id='modify_data')

'''ComSet'''

class ComsetForm(FlaskForm):
    
    comset_1 = StringField('CommSet1:',id = 'comset_1',validators = [Required()],
                             render_kw={'placeholder':','.join(['if0001']),'value':'if0001'})
                             
    comset_2 = StringField('CommSet2:',id = 'comset_2',validators = [Required()],
                             render_kw={'placeholder':','.join(['if0001','if0002']),'value':'if0001,if0002'})  
    
    comset_3 = StringField('CommSet3:',id = 'comset_3',validators = [Required()],
                         render_kw={'placeholder':','.join(['if0002']),'value':'if0002'})
    
    submit4  =  SubmitField('submit',id='submit_comset')
    
class ModifyComsetForm(FlaskForm):  
    
    submit5 = SubmitField('Modify',id='modify_comset')
  
'''Global Config '''   

class GlobalConfigForm(FlaskForm):
    
    start_spot= IntegerField('start_spot',id = 'start_spot',validators=[],
                           render_kw={'placeholder': 0},default = 0)
    
    end_spot  = IntegerField('end_spot', id = 'end_spot',validators=[],
                           render_kw={'placeholder': 32000},default = 32000)
    
    spot_step = IntegerField('spot_step', id = 'spot_step',validators=[],
                           render_kw={'placeholder': 1},default = 1) 
    
    com_set   = IntegerField('comm_set', id = 'comset',validators=[],
                           render_kw={'placeholder': 1},default = 1) 
    
    slipage   = IntegerField('slipage', id = 'slipge',validators=[],
                           render_kw={'placeholder': 'N (base point)'},default = 0) 
    
    exec_algo = RadioField('exec_method',  id = 'exec_method',validators=[],
                        choices = [('OpponentPrc','OpponentPrc'),('LastPrc','LastPrc')],
                        default = 'LastPrc'
                        )
    
    dual_mode = RadioField('entry_mode',  id = 'entry_mode',validators=[],
                        choices = [('BothSide','BothSide'),('SingleSide','SingleSide')],
                        default = 'SingleSide'
                        )
    
    submit6   = SubmitField('submit',id='submit_global_config')
    
class ModifyGlobalConfigForm(FlaskForm):
    
    submit7   = SubmitField('Modify',id='modify_global_config')
    
''' Entry Rules '''
class ResetEntryRules(FlaskForm):
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
    
class EntryRuleForm(RuleForm):
    add_entry_rule  = SubmitField('add_entry_rule',id = 'add_entry_rule')
    
''' ExitRules '''
class ExitRuleForm(RuleForm):
    add_exit_rule  = SubmitField('add_exit_rule',id = 'add_exit_rule')
    
class ResetExitRules(FlaskForm):
    reset_exit_rules = SubmitField('reset_all',id = 'reset_exit_rules')

class SubmitForm(FlaskForm):
    
    submit1 = SubmitField('Run',id='submit_backtest')
     



