from flask import render_template, redirect, request, url_for, flash, session, g 
from flask_login import login_user, logout_user, login_required, current_user,fresh_login_required
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm,SubmitForm,DataForm,ModifyDataForm,UploadForm()

def generate_block(cookie,data_form):
    start_date,end_date = data_form.start_date.data,data_form.end_date.data
    adjust,type,level = data_form.adjust.data,data_form.type.data,data_form.level.data
    indicators = ','.join(data_form.indicators.data)
    instruments = ','.join(data_form.instruments.data)
#     print start_date,end_date,adjust,type,level,indicators,instruments
    cookie['start_date'],cookie['end_date'],cookie['adjust'],cookie['type'],cookie['level'] = start_date,end_date,adjust,type,level
    cookie['indicators'],cookie['instruments'] = indicators,instruments
    return True

@auth.context_processor
def inject_var():
    ret = {}
    if 'verify' in session:
        ret['verify'] = session['verify']
    if 'data_block' in session:
        ret['data_block'] = session['data_block']
    if 'config_ready' in session:
        ret['config_ready'] = session['config_ready']
    return ret

def check_backtest(cookie):
    if 'verify' in cookie:
        for k,v in cookie['verify'].iteritems():
            if not v:
                return False
        cookie['config_ready'] = True
        return True
    return False

def init_session(cookie):
    
    if 'verify' not in cookie:
        cookie['verify'] = {}
        cookie['verify']['data'] = False
        cookie['verify']['global'] = False
        cookie['verify']['entry'] = False
        cookie['verify']['exit'] = False
        cookie['verify']['set'] = False
    
    if 'data_block' not in cookie:
        cookie['data_block'] = {}
    
    if 'config_ready' not in cookie:    
        cookie['config_ready'] = False
        
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    init_session(session)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@fresh_login_required
@auth.route('/fill',methods = ['GET','POST'])
def fill():
    sub_form = SubmitForm()
    data_form = DataForm()
    modify_form = ModifyDataForm()
    upload_instruments = UploadForm()
    
    if sub_form.submit1.data and sub_form.validate_on_submit():
        flash('Ready to back Testing')
    
    return render_template('auth/fill.html',submit_form = sub_form,data_form = data_form,modify_form = modify_form)

@fresh_login_required
@auth.route('/fill_data',methods = ['GET','POST'])
def fill_data():
    sub_form = SubmitForm()
    data_form = DataForm()
    modify_form = ModifyDataForm()
    upload_instruments = UploadForm()

    if data_form.submit2.data and data_form.validate_on_submit():
        flash('Ready to Create Data Block')
        if generate_block(session['data_block'],data_form):
            session['verify']['data'] = True
            check_backtest(session)
        else:
            session['verify']['data'] = False
            
    args = {}
    args['submit_form'],args['data_form'],args['modify_form'] = sub_form, data_form, modify_form
    return render_template('auth/fill.html',**args)
    
@fresh_login_required
@auth.route('/modify_data',methods = ['GET','POST'])
def modify_data():
    modify_form = ModifyDataForm()
    data_form = DataForm()
    
    session['verify']['data'] = False
    session['config_ready'] = False
    if modify_form.submit3.data and modify_form.validate_on_submit():
        flash('modify data block')
        
    args = {}
    args['data_form'],args['modify_form'] = data_form,modify_form    
    return render_template('auth/fill.html',**args)



