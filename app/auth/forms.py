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
                             render_kw={'readOnly': "true",'placeholder':','.join(basic_indicators)},
                             default = ','.join(basic_indicators) )
    
    instruments = SelectMultipleField('instruments', id = 'instruments',
                            choices = [('if0001','if0001'),
                                       ('if0002','if0002'),],
                            default = ('if0001','if0002'))
    
    #or_upload_file = FileField(validators=[FileAllowed(ufile, 'TXT allowed'),])
    submit2     =  SubmitField('generate',id='generate_data')
    
class ModifyDataForm(FlaskForm):
    
    submit3 = SubmitField('ModifyData',id='modify_data')

'''ComSet'''

class ComsetForm(FlaskForm):
    
    comset_1 = StringField('CommSet1:',id = 'comset_1',validators = [],
                             render_kw={'placeholder':','.join(['if0001'])},
                             default = ','.join(['if0001']) )
                             
    comset_2 = StringField('CommSet2:',id = 'comset_2',validators = [],
                             render_kw={'placeholder':','.join(['if0001','if0002'])},
                             default = ','.join(['if0001','if0002']) )  
    
    comset_3 = StringField('CommSet3:',id = 'comset_3',validators = [],
                         render_kw={'placeholder':','.join(['if0002'])},
                         default = ','.join(['if0002']) )
    
    submit4  =  SubmitField('submit',id='submit_comset')
    
class ModifyComsetForm(FlaskForm):  
    
    submit5 = SubmitField('Modify',id='modify_comset')
  
'''Global Config '''   

class GlobalConfigForm(FlaskForm):
    pass

class ModifyGlobalConfigForm(FlaskForm):
    pass
   
class SubmitForm(FlaskForm):
    
    submit1 = SubmitField('Run',id='submit_backtest')
     



