from flask import render_template, redirect, request, url_for, flash, session, g 
from flask_login import login_user, logout_user, login_required, current_user,fresh_login_required
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm,SubmitForm,DataForm,ModifyDataForm,ComsetForm,ModifyComsetForm,\
                    GlobalConfigForm,ModifyGlobalConfigForm
from .. import ufile

def web_global_config_to_server_global_config(global_config_dict):
    server_dict = {}
    for k,v in global_config_dict.iteritems():
        if str(k) == 'exec_method':
            server_dict['exec_algo'] = str(v)
        elif str(k) == 'entry_mode':
            server_dict['dual_mode'] = 1 if v == 'BothSide' else 0
        else:
            server_dict[str(k)] = v
    return server_dict
        
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
#     print 'block_dict = ',block_dict
#     print 'server_dict = ',server_block
    return server_block

def web_comset_data_to_server_data(web_dict):
    server_data = {}
    for k,v in web_dict.iteritems():
        if len(v) > 0:
            server_data[str(k)] = str(v).split()
    return server_data        
            
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
    cookie[1] = comset_form.comset_1.data
    cookie[2] = comset_form.comset_2.data
    cookie[3] = comset_form.comset_3.data
    return 0

def generate_global_config(cookie,global_config_form):
    cookie['start_spot'],cookie['end_spot'],cookie['spot_step'] = \
        global_config_form.start_spot.data,global_config_form.end_spot.data,global_config_form.spot_step.data
    cookie['sipage'] =  global_config_form.slipage.data
    cookie['exec_algo'] = global_config_form.exec_algo.data
    cookie['com_set'] =  global_config_form.com_set.data
    cookie['dual_mode'] = global_config_form.dual_mode.data
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
    if 'global_config' in session:
        ret['global_config'] = session['global_config']
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
        cookie['verify']['global_config'] = False
        cookie['verify']['entry'] = False
        cookie['verify']['exit'] = False
        cookie['verify']['set'] = False
    
    if 'data_block' not in cookie:
        cookie['data_block'] = {}  
    if 'comset' not in cookie:
        cookie['comset'] = {}
    if 'global_config' not in cookie:
        cookie['global_config'] = {}
    
    #for upload instruments files
#     if 'upload_inss_name' not in cookie:
#         cookie['upload_inss_name'] = None

def get_main_page_arg_dict(*forms):
    args = {}
    args['submit_form'],args['data_form'],args['modify_data_form'],\
            args['comset_form'],args['modify_comset_form'],\
            args['global_config_form'],args['modify_global_config_form'] \
        = forms[0],forms[1],forms[2],forms[3],forms[4],forms[5],forms[6]
    return args

###----------------------------------------------------------------------------
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

###----------------------------------------------------------------------------
''' For basic UI '''
@login_required
@auth.route('/fill',methods = ['GET','POST'])
def fill():
    sub_form = SubmitForm()
    data_form,modify_data_form = DataForm(),ModifyDataForm()
    comset_form,modify_comset_form = ComsetForm(),ModifyComsetForm()
    global_config_form,modify_global_config_form = GlobalConfigForm(),ModifyGlobalConfigForm()
    
    if sub_form.submit1.data and sub_form.validate_on_submit():
        flash('Start back Testing, please wait for a while...')
    
    args = get_main_page_arg_dict(sub_form, data_form, \
                                  modify_data_form,comset_form,modify_comset_form,\
                                  global_config_form,modify_global_config_form)
    return render_template('auth/fill.html',**args)

###----------------------------------------------------------------------------
''' For Shm Block Data'''
@login_required
@auth.route('/fill_data',methods = ['POST',])
def fill_data():
    sub_form = SubmitForm()
    data_form,modify_data_form = DataForm(),ModifyDataForm()
    comset_form,modify_comset_form = ComsetForm(),ModifyComsetForm()
    global_config_form,modify_global_config_form = GlobalConfigForm(),ModifyGlobalConfigForm()
    
    if data_form.submit2.data and data_form.validate_on_submit():
        flash('Set Data Block')
        if generate_block(session['data_block'],data_form) == 0:
            session['verify']['data'] = True
#             web_datablock_to_server_datablock(session['data_block'])
        else:
            session['verify']['data'] = False
            
#         if data_form.or_upload_file.data:   
#             filename = ufile.save(data_form.or_upload_file.data)
#             session['upload_inss_name'] = filename
#             file_url = ufile.url(filename)

    args = get_main_page_arg_dict(sub_form, data_form, \
                                  modify_data_form,comset_form,modify_comset_form,\
                                  global_config_form,modify_global_config_form) 
    return render_template('auth/fill.html',**args)
    
@login_required
@auth.route('/modify_data',methods = ['POST',])
def modify_data():
    modify_form = ModifyDataForm()
    session['verify']['data'] = False
    if modify_form.submit3.data and modify_form.validate_on_submit():
        flash('Modify data block')
    return redirect(url_for('auth.fill'))

###----------------------------------------------------------------------------
''' For Comset Data'''
@login_required
@auth.route('/fill_comset_data',methods = ['POST',])
def fill_comset_data():
    sub_form = SubmitForm()
    data_form,modify_data_form = DataForm(),ModifyDataForm()
    comset_form,modify_comset_form = ComsetForm(),ModifyComsetForm()
    global_config_form,modify_global_config_form = GlobalConfigForm(),ModifyGlobalConfigForm()
    
    if comset_form.submit4.data and comset_form.validate_on_submit():
        flash('Set commodity set')
        if generate_comset(session['comset'],comset_form) == 0:
            session['verify']['set'] = True
        else:
            session['verify']['set'] = False
            
    args = get_main_page_arg_dict(sub_form, data_form, \
                                  modify_data_form,comset_form,modify_comset_form,\
                                  global_config_form,modify_global_config_form)  
    return render_template('auth/fill.html',**args)

@login_required
@auth.route('/modify_comset_data',methods = ['POST',])
def modify_comset_data():
    modify_form = ModifyComsetForm()
    session['verify']['set'] = False
    if modify_form.submit5.data and modify_form.validate_on_submit():
        flash('Modify commodity set')
    return redirect(url_for('auth.fill'))

###----------------------------------------------------------------------------
''' For Global Config '''
@login_required
@auth.route('/fill_global_config_data',methods = ['POST',])
def fill_global_config_data():
    sub_form = SubmitForm()
    data_form,modify_data_form = DataForm(),ModifyDataForm()
    comset_form,modify_comset_form = ComsetForm(),ModifyComsetForm()
    global_config_form,modify_global_config_form = GlobalConfigForm(),ModifyGlobalConfigForm()
    
    if global_config_form.submit6.data and global_config_form.validate_on_submit():
        flash('Set Global Config')
        if generate_global_config(session['global_config'],global_config_form) == 0:
            session['verify']['global_config'] = True
        else:
            session['verify']['global_config'] = False
            
    args = get_main_page_arg_dict(sub_form, data_form, \
                                  modify_data_form,comset_form,modify_comset_form,\
                                  global_config_form,modify_global_config_form)  
    return render_template('auth/fill.html',**args)

@login_required
@auth.route('/modify_global_config_data',methods = ['POST',])
def modify_global_config_data():
    modify_form = ModifyGlobalConfigForm()
    session['verify']['global_config'] = False
    if modify_form.submit7.data and modify_form.validate_on_submit():
        flash('Modify global config')
    return redirect(url_for('auth.fill'))

