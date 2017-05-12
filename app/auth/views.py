from flask import render_template, redirect, request, url_for, flash, session, g 
from flask_login import login_user, logout_user, login_required, current_user,fresh_login_required
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm,SubmitForm,DataForm,ModifyDataForm,ComsetForm,ModifyComsetForm,\
                    GlobalConfigForm,ModifyGlobalConfigForm,\
                    ResetEntryRules, EntryRuleForm, ResetExitRules, ExitRuleForm
from .. import ufile 

def web_conditions_to_server_conditions(conditions):
    server_dict = {}
    keys = ('op','fid','flip','gap1','offset1','lothr','hithr','param0','param1','param2','param3','param4')
    for row,icond in enumerate(conditions):
        server_dict[row] = dict(zip(keys,icond))
        server_dict[row]['gap2'] = 0
        server_dict[row]['offset2'] = 0
    return server_dict
    
def web_global_config_to_server_global_config(global_config_dict):
    server_dict = {}
    for k,v in global_config_dict.iteritems():
        if str(k) == 'exec_method':
            server_dict['exec_algo'] = 'LAST' if str(v) == 'LastPrc' else 'SIDE'
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
            
def generate_block(data_form):
    cookie = session['data_block']
    start_date,end_date = data_form.start_date.data,data_form.end_date.data
    adjust,level = data_form.adjust.data,data_form.level.data
    indicators = data_form.indicators.data
    instruments = ','.join(data_form.instruments.data)
    cookie['start_date'],cookie['end_date'],cookie['adjust'],cookie['level'] = \
                        start_date,end_date,adjust,level
    cookie['indicators'],cookie['instruments'] = indicators,instruments
    return 0

def generate_comset(comset_form):
    print comset_form.comset_1.data,'\t',comset_form.comset_2.data,'\t',comset_form.comset_3.data
    cookie = session['comset']
    cookie['1'] = comset_form.comset_1.data
    cookie['2'] = comset_form.comset_2.data
    cookie['3'] = comset_form.comset_3.data
    return 0

def generate_global_config(global_config_form):
    cookie = session['global_config']
    cookie['start_spot'],cookie['end_spot'],cookie['spot_step'] = \
        global_config_form.start_spot.data,global_config_form.end_spot.data,global_config_form.spot_step.data
    cookie['slipage'] =  global_config_form.slipage.data
    cookie['exec_algo'] = global_config_form.exec_algo.data
    cookie['com_set'] =  global_config_form.com_set.data
    cookie['dual_mode'] = global_config_form.dual_mode.data
    cookie['direction'] = global_config_form.direction.data
    cookie['quant'] = global_config_form.quant.data
    cookie['minTTL'] = global_config_form.minTTL.data
    cookie['maxTTL'] = global_config_form.maxTTL.data
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
    if 'entry_conditions' in session:
        ret['entry_conditions'] = session['entry_conditions']
        ret['entry_condtion_values'] = [session['entry_conditions'][str(i)] for i in range(session['entry_conditions']['entry_nconds'])]
    if 'exit_conditions' in session:
        ret['exit_conditions'] = session['exit_conditions']
        ret['exit_condtion_values'] = [session['exit_conditions'][str(i)] for i in range(session['exit_conditions']['exit_nconds'])]
       
    if session['entry_conditions']['entry_nconds'] > 0:
        session['verify']['entry'] = True
    else:
        session['verify']['entry'] = False
    if session['exit_conditions']['exit_nconds'] > 0:
        session['verify']['exit'] = True
    else:
        session['verify']['exit'] = False
        
    ret['backtest_ready'] = check_backtest(session)
    if ret['backtest_ready']: session['show_tab'] = ()
    if 'show_tab' in session:
        ret['show_tab'] = session['show_tab']    
    return ret

def check_backtest(cookie):
    if 'verify' in cookie:
        for k,v in cookie['verify'].iteritems():
            if not v:
                return False
        return True
    return False

def init_session(cookie,force_reset = False):
    
    if 'verify' not in cookie or force_reset:
        cookie['verify'] = {}
        cookie['verify']['data'] = False
        cookie['verify']['global_config'] = False
        cookie['verify']['entry'] = False
        cookie['verify']['exit'] = False
        cookie['verify']['set'] = False
    
    if 'data_block' not in cookie or force_reset:
        cookie['data_block'] = {}  
    if 'comset' not in cookie or force_reset:
        cookie['comset'] = {}
    if 'global_config' not in cookie or force_reset:
        cookie['global_config'] = {}
        
    if 'entry_conditions' not in cookie or force_reset:
        cookie['entry_conditions'] = {}
        cookie['entry_conditions']['entry_nconds'] = 2
        cookie['entry_conditions']['0'] = ('AND',11000,0,0,0,-0.1,0.1,120,0,0,0,0)
        cookie['entry_conditions']['1'] = ('AND',1500,0,0,0,0,98,5,0,0,0,0)
        
    if 'exit_conditions' not in cookie or force_reset:
        cookie['exit_conditions'] = {}
        cookie['exit_conditions']['exit_nconds'] = 2
        cookie['exit_conditions']['0'] = ('OR',1500,0,0,0,1.99,'inf',6,0,0,0,0)
        cookie['exit_conditions']['1'] = ('OR',1500,0,0,0,-1.99,'inf',4,0,0,0,0)
    
    if 'show_tab' not in cookie or force_reset:
        cookie['show_tab'] = ('data',)
    
    #for upload instruments files
#     if 'upload_inss_name' not in cookie:
#         cookie['upload_inss_name'] = None

def get_main_page_arg_dict(*forms):
    args = {}
    args['submit_form'],args['data_form'],args['modify_data_form'],\
            args['comset_form'],args['modify_comset_form'],\
            args['global_config_form'],args['modify_global_config_form'],\
            args['reset_entry_rule_form'],args['add_entry_rule_form'],\
            args['reset_exit_rule_form'],args['add_exit_rule_form'] \
        = forms[0],forms[1],forms[2],forms[3],forms[4],forms[5],forms[6],\
            forms[7],forms[8],forms[9],forms[10]
    return args

def get_main_page_form_obj():
    return ( SubmitForm(),DataForm(),ModifyDataForm(),\
                        ComsetForm(),ModifyComsetForm(),\
                        GlobalConfigForm(),ModifyGlobalConfigForm(),\
                        ResetEntryRules(),EntryRuleForm(),\
                        ResetExitRules(),ExitRuleForm() )
                        
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
    main_page_forms = get_main_page_form_obj()
    sub_form = main_page_forms[0]
    
    if check_backtest(session) is True:
        session['show_tab'] = ()
        
    if sub_form.submit1.data and sub_form.validate_on_submit():
        flash('Start back Testing, please wait for a while...')
    
    args = get_main_page_arg_dict(*main_page_forms)
    return render_template('auth/fill.html',**args)

###----------------------------------------------------------------------------
''' For Shm Block Data'''
@login_required
@auth.route('/fill_data',methods = ['POST','GET'])
def fill_data():
    main_page_forms = get_main_page_form_obj()
    data_form = main_page_forms[1]
    session['show_tab'] = ('data',)
    if data_form.submit2.data and data_form.validate_on_submit():
        flash('Set Data Block')
        if generate_block(data_form) == 0:
            session['verify']['data'] = True
        else:
            session['verify']['data'] = False
            flash('Please Check Data Parameters Again')
            
#         if data_form.or_upload_file.data:   
#             filename = ufile.save(data_form.or_upload_file.data)
#             session['upload_inss_name'] = filename
#             file_url = ufile.url(filename)

    args = get_main_page_arg_dict(*main_page_forms) 
    return render_template('auth/fill.html',**args)
    
@login_required
@auth.route('/modify_data',methods = ['POST','GET'])
def modify_data():
    modify_form = ModifyDataForm()
    session['verify']['data'] = False
    session['show_tab'] = ('data',)
    if modify_form.submit3.data and modify_form.validate_on_submit():
        flash('Modify data block')
    return redirect(url_for('auth.fill'))

###----------------------------------------------------------------------------
''' For Comset Data'''
@login_required
@auth.route('/fill_comset_data',methods = ['POST','GET'])
def fill_comset_data():
    main_page_forms = get_main_page_form_obj()
    comset_form = main_page_forms[3]
    session['show_tab'] = ('com_set',)
    if comset_form.submit4.data and comset_form.validate_on_submit():
        flash('Set commodity set')
        if generate_comset(comset_form) == 0:
            session['verify']['set'] = True
        else:
            session['verify']['set'] = False
            flash('Please Check Comset Parameters Again~')
    args = get_main_page_arg_dict(*main_page_forms)   
    return render_template('auth/fill.html',**args)

@login_required
@auth.route('/modify_comset_data',methods = ['POST','GET'])
def modify_comset_data():
    modify_form = ModifyComsetForm()
    session['verify']['set'] = False
    session['show_tab'] = ('com_set',)
    if modify_form.submit5.data and modify_form.validate_on_submit():
        flash('Modify commodity set')
    return redirect(url_for('auth.fill'))

###----------------------------------------------------------------------------
''' For Global Config '''
@login_required
@auth.route('/fill_global_config_data',methods = ['POST','GET'])
def fill_global_config_data():
    main_page_forms = get_main_page_form_obj()
    global_config_form = main_page_forms[5]
    print 'fuck! ',global_config_form.submit6.data
    print 'You! ',global_config_form.is_submitted(),global_config_form.validate()
    session['show_tab'] = ('global_config',)
    if global_config_form.submit6.data and global_config_form.validate_on_submit():
        flash('Set Global Config')
        if generate_global_config(global_config_form) == 0:
            session['verify']['global_config'] = True
        else:
            session['verify']['global_config'] = False
            flash('Please Check Config Parameters Again')
    elif global_config_form.submit6.data and global_config_form.is_submitted() and not global_config_form.validate():
            flash('Please Check Config Parameters Again')
            
    args = get_main_page_arg_dict(*main_page_forms) 
    return render_template('auth/fill.html',**args)

@login_required
@auth.route('/modify_global_config_data',methods = ['POST','GET'])
def modify_global_config_data():
    modify_form = ModifyGlobalConfigForm()
    session['verify']['global_config'] = False
    session['show_tab'] = ('global_config',)
    if modify_form.submit7.data and modify_form.validate_on_submit():
        flash('Modify global config')
    return redirect(url_for('auth.fill'))

###----------------------------------------------------------------------------
'''for EntryRules'''
@login_required
@auth.route('/fill_entry_rule_data',methods = ['POST','GET'])
def fill_entry_rule_data():
    main_page_forms = get_main_page_form_obj()
    reset_rules = main_page_forms[7]
    rule_form = main_page_forms[8]
    conditions = session['entry_conditions']
    
    print reset_rules.reset_entry_rules.data,reset_rules.is_submitted(),reset_rules.validate()
    print rule_form.add_entry_rule.data,rule_form.is_submitted(),rule_form.validate()
    
    session['show_tab'] = ('entry',)
    if reset_rules.reset_entry_rules.data and reset_rules.validate_on_submit():
        flash('reset all entry rules')
        conditions = {}
        session['entry_conditions']['entry_nconds'] = 0
    elif rule_form.add_entry_rule.data and rule_form.validate_on_submit():
        values = ( rule_form.logic.data,rule_form.condID.data,rule_form.flip.data,rule_form.gap.data,rule_form.offset.data,\
                  rule_form.lowthrs.data,rule_form.highthrs.data,\
                   rule_form.para1.data,rule_form.para2.data,rule_form.para3.data,rule_form.para4.data,rule_form.para5.data )
        conditions[str(session['entry_conditions']['entry_nconds'])] = values
        session['entry_conditions']['entry_nconds'] += 1
        flash('add new entry rule')
    elif rule_form.is_submitted() and not rule_form.validate():
        flash('please check the new entry rule again~')
            
    args = get_main_page_arg_dict(*main_page_forms) 
    return render_template('auth/fill.html',**args)

###----------------------------------------------------------------------------
'''for ExitRules'''
@login_required
@auth.route('/fill_exit_rule_data',methods = ['POST','GET'])
def fill_exit_rule_data():
    main_page_forms = get_main_page_form_obj()
    reset_rules = main_page_forms[9]
    rule_form = main_page_forms[10]
    conditions = session['exit_conditions']
    
    print reset_rules.reset_exit_rules.data,reset_rules.is_submitted(),reset_rules.validate()
    print rule_form.add_exit_rule.data,rule_form.is_submitted(),rule_form.validate()
    
    session['show_tab'] = ('exit',)
    if reset_rules.reset_exit_rules.data and reset_rules.validate_on_submit():
        flash('reset_all_rules')
        conditions = {}
        session['exit_conditions']['exit_nconds'] = 0
    elif rule_form.add_exit_rule.data and rule_form.validate_on_submit():
        values = ( rule_form.logic.data,rule_form.condID.data,rule_form.flip.data,rule_form.gap.data,rule_form.offset.data,\
                  rule_form.lowthrs.data,rule_form.highthrs.data,\
                   rule_form.para1.data,rule_form.para2.data,rule_form.para3.data,rule_form.para4.data,rule_form.para5.data )
        conditions[str(session['exit_conditions']['exit_nconds'])] = values
        session['exit_conditions']['exit_nconds'] += 1
        flash('add new exit rule')
    elif rule_form.is_submitted() and not rule_form.validate():
        flash('please check the new exit rule again~')
            
    args = get_main_page_arg_dict(*main_page_forms) 
    return render_template('auth/fill.html',**args)

###-------------------------------------------------------------------------------
###clear all conditions
@login_required
@auth.route('/reset_all',methods = ['POST','GET'])
def reset_all():
    init_session(session,force_reset = True) 
    flash('All parameters have been reset!')
    return redirect(url_for('auth.fill'))


