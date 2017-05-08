from flask import render_template, redirect, request, url_for, flash, session, g 
from flask_login import login_user, logout_user, login_required, current_user,fresh_login_required
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm,SubmitForm,DataForm,ModifyDataForm,ComsetForm,ModifyComsetForm
from .. import ufile

def web_datablock_to_server_datablock(block_dict):
    server_block = {}
    for k,v in block_dict.iteritems():
        if str(k) == 'indicators' or str(k) == 'instruments':
            server_block[str(k)] = str(v).split(',')[:]
        elif str(k) == 'adjust': 
            server_block[str(k)] = 0 if v == 'no' else 1
        else:
            server_block[str(k)] = str(v)
    if 'type' not in block_dict:
        server_block['type'] = 'future'
    print 'block_dict = ',block_dict
    print 'server_dict = ',server_block
    return server_block

def generate_block(cookie,data_form):
    start_date,end_date = data_form.start_date.data,data_form.end_date.data
    adjust,level = data_form.adjust.data,data_form.level.data
    indicators = data_form.indicators.data
    instruments = ','.join(data_form.instruments.data)
    cookie['start_date'],cookie['end_date'],cookie['adjust'],cookie['level'] = \
                        start_date,end_date,adjust,level
    cookie['indicators'],cookie['instruments'] = indicators,instruments
    return 0

def generate_comset(cookie,comset_form):
    cookie[1] = comset_form.comset_1
    cookie[2] = comset_form.comset_2
    cookie[3] = comset_form.comset_3
    return 0

@auth.context_processor
def inject_var():
    ret = {}
    if 'verify' in session:
        ret['verify'] = session['verify']
    if 'data_block' in session:
        ret['data_block'] = session['data_block']
    if 'comset' in session:
        ret['comset'] = session['comset']
    return ret

def check_backtest(cookie):
    if 'verify' in cookie:
        for k,v in cookie['verify'].iteritems():
            if not v:
                return False
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
    if 'comset' not in cookie:
        cookie['comset'] = {}
    
    #for upload instruments files
#     if 'upload_inss_name' not in cookie:
#         cookie['upload_inss_name'] = None

''' For log in '''       
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    init_session(session)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
#             login_user(user, form.remember_me.data)
            login_user(user, False)
            return redirect(url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

''' For basic UI '''
@login_required
@auth.route('/fill',methods = ['GET','POST'])
def fill():
    sub_form = SubmitForm()
    data_form,modify_data_form = DataForm(),ModifyDataForm()
    comset_form,modify_comset_form = ComsetForm(),ModifyComsetForm()
    
    if sub_form.submit1.data and sub_form.validate_on_submit():
        flash('Ready to back Testing')
    
    args = {}
    args['submit_form'],args['data_form'],args['modify_data_form'],\
                        args['comset_form'],args['modify_comset_form']\
        = sub_form, data_form, modify_data_form,comset_form,modify_comset_form
    return render_template('auth/fill.html',**args)

''' For Shm Block Data'''
@login_required
@auth.route('/fill_data',methods = ['POST',])
def fill_data():
    sub_form = SubmitForm()
    data_form,modify_data_form = DataForm(),ModifyDataForm()
    comset_form,modify_comset_form = ComsetForm(),ModifyComsetForm()
    
    if data_form.submit2.data and data_form.validate_on_submit():
        flash('Ready to Create Data Block')
        if generate_block(session['data_block'],data_form) == 0:
            session['verify']['data'] = True
            web_datablock_to_server_datablock(session['data_block'])
        else:
            session['verify']['data'] = False
            
#         if data_form.or_upload_file.data:   
#             filename = ufile.save(data_form.or_upload_file.data)
#             session['upload_inss_name'] = filename
#             file_url = ufile.url(filename)

    args = {}
    args['submit_form'],args['data_form'],args['modify_data_form'],\
                        args['comset_form'],args['modify_comset_form']\
        = sub_form, data_form, modify_data_form,comset_form,modify_comset_form 
    return render_template('auth/fill.html',**args)
    
@login_required
@auth.route('/modify_data',methods = ['POST',])
def modify_data():
    modify_form = ModifyDataForm()
    session['verify']['data'] = False
    if modify_form.submit3.data and modify_form.validate_on_submit():
        flash('modify data block')
    return redirect(url_for('auth.fill'))

''' For Comset Data'''
@login_required
@auth.route('/fill_comset_data',methods = ['POST',])
def fill_comset_data():
    sub_form = SubmitForm()
    data_form,modify_data_form = DataForm(),ModifyDataForm()
    comset_form,modify_comset_form = ComsetForm(),ModifyComsetForm()
    
    if comset_form.submit4.data and comset_form.validate_on_submit():
        flash('Ready to generata commodity set')
        if generate_comset(session['comset'],comset_form) == 0:
            session['verify']['set'] = True
        else:
            session['verify']['set'] = False
            
    args = {}
    args['submit_form'],args['data_form'],args['modify_data_form'],\
                        args['comset_form'],args['modify_comset_form']\
        = sub_form, data_form, modify_data_form,comset_form,modify_comset_form 
    return render_template('auth/fill.html',**args)

@login_required
@auth.route('/modify_comset_data',methods = ['POST',])
def modify_comset_data():
    modify_form = ModifyComsetForm()
    session['verify']['set'] = False
    if modify_form.submit3.data and modify_form.validate_on_submit():
        flash('modify commodity set')
    return redirect(url_for('auth.fill'))


