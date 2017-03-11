from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, RadioField, SelectMultipleField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    
    username = StringField('UserName', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required(), Length(1, 64)])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')
           
class DataForm(FlaskForm):
    
    start_date = DateField('start_date',id = 'start_date',validators=[Required()])
    end_date   = DateField('end_date', id = 'end_date',validators=[Required()])
    level      = RadioField('level', id = 'level',validators=[Required()],
                            choices = [('tick','tick'),
                                       ('1min','1min'),
                                       ('5min','5min'),
                                       ('day','day')],
                            default = 'tick'
                            )
    adjust     = RadioField('adjust', id = 'adjust',validators=[Required()],
                            choices = [('yes','yes'),
                                       ('no','no')],
                            default = 'no'
                            )
    type       = RadioField('type', id = 'type',validators=[Required()],
                            choices = [('stock','stock'),
                                       ('future','future')],
                            default = 'future'
                            )
    indicators = SelectMultipleField('indicators', id = 'indicators',validators=[Required()],
                             choices = [('lastPrice','lastPrice'),
                                       ('culVolume','culVolume')],
                                     )
    instruments = SelectMultipleField('instruments', id = 'instruments',validators=[Required()],
                            choices = [('if0001','if0001'),
                                       ('if0002','if0002')],
                                      )
    submit     =  SubmitField('generate',id='generate')
    
class SubmitForm(FlaskForm):
    
    submit = SubmitField('Run',id='submit_backtest')


