from flask import render_template, redirect, request, url_for, flash, session, g, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user, fresh_login_required
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm,SubmitForm,\
                    IndexFutureDataForm,CommodityFutureDataForm,StockIndexDataForm,ModifyDataForm,\
                    IndexFutureComsetForm,CommodityFutureFutureComsetForm,StockComsetForm,ModifyComsetForm,\
                    GlobalConfigForm,ModifyGlobalConfigForm,\
                    EntryRuleForm, ExitRuleForm  
comset_forms = [IndexFutureComsetForm,CommodityFutureFutureComsetForm,StockComsetForm]
data_forms = [IndexFutureDataForm,CommodityFutureDataForm,StockIndexDataForm]

from .. import ufile
import os
import json

import sys
upper_abs_path = os.path.sep.join(
    (os.path.abspath(os.curdir).split(os.path.sep)[:-1]))
pkg_path = os.path.join(upper_abs_path, 'generate_data_block')
# print pkg_path
if pkg_path not in sys.path:
    sys.path.append(pkg_path)

from misc import get_today, get_hourminsec, unicode2str
from ui_misc import diff_seconds,error_code_dict 
from transfer import get_server_result_path
from const_vars import Ticker
from pta import get_summarys
from pta import parser as output_parser
from data_center_config import future_indicators_tick, future_indicators_min, stock_all_indicators

keys = ('op', 'fid', 'flip', 'gap1', 'offset1', 'lothr', 'hithr', 'param0',
        'param1', 'param2', 'param3', 'param4')


def web_conditions_to_server_conditions(conditions):
    server_dict = {}
    row = 0
    global keys
    for key, icond in conditions.iteritems():
        if not key.endswith('_nconds'):
            server_dict[row] = dict(zip(keys, icond))
            server_dict[row]['gap2'] = 0
            server_dict[row]['offset2'] = 0
            row += 1
    return server_dict


def web_conditions_to_server_conditions_entry(conditions, direction, quant):
    entry_dict = {}
    entry_dict['conditions'] = web_conditions_to_server_conditions(conditions)
    entry_dict['direction'] = direction
    entry_dict['quant'] = quant
    return entry_dict


def web_conditions_to_server_conditions_exit(conditions, minTTL, maxTTL):
    exit_dict = {}
    exit_dict['conditions'] = web_conditions_to_server_conditions(conditions)
    exit_dict['minTTL'] = minTTL
    exit_dict['maxTTL'] = maxTTL
    return exit_dict


def web_global_config_to_server_global_config(global_config_dict):
    server_dict = {}
    for k, v in global_config_dict.iteritems():
        if str(k) == 'exec_algo':
            server_dict['exec_algo'] = 'LAST' if str(v) == 'LastPrc' else 'SIDE'
        elif str(k) == 'dual_mode':
            server_dict['dual_mode'] = 1 if v == 'BothSide' else 0
        else:
            server_dict[str(k)] = v
    return server_dict


def web_datablock_to_server_datablock(block_dict):
    server_block = {}
    for k, v in block_dict.iteritems():
        if str(k) == 'indicators' or str(k) == 'instruments':
            server_block[str(k)] = map(lambda x: str.lower(x),
                                       str(v).split(',')[:])
        elif str(k) == 'adjust':
            server_block[str(k)] = 0 if v == 'no' else 1
        else:
            server_block[str(k)] = str(v)
    if 'type' not in block_dict:
        if session['mode'] == 0 or session['mode'] == 1:
            server_block['type'] = 'future'
        else:
            server_block['type'] = 'stock'

#     print 'block_dict = ',block_dict
#     print 'server_dict = ',server_block
    return server_block


def web_comset_data_to_server_data(web_dict):
    server_data = {}
    if session['mode'] == 0 or session['mode'] == 1:
        ticker = Ticker()
        for k, v in web_dict.iteritems():
            if len(v) > 0:
                server_data[str(k)] = map(ticker.get_id, str(v).split(','))
        return server_data
    else:
        for k, v in web_dict.iteritems():
            server_data[str(k)] = str(v).split(',')
        return server_data


def generate_block(data_form):
    cookie = session['data_block']
    start_date, end_date = data_form.start_date.data, data_form.end_date.data
    adjust, level = data_form.adjust.data, data_form.level.data
    indicators = data_form.indicators.data
    instruments = ','.join(data_form.instruments.data)
    cookie['start_date'],cookie['end_date'],cookie['adjust'],cookie['level'] = \
                        start_date,end_date,adjust,level
    cookie['indicators'], cookie['instruments'] = indicators, instruments
    return 0


def generate_comset(comset_form):
#     print comset_form.comset_1.data,'\t',comset_form.comset_2.data,'\t',comset_form.comset_3.data
    cookie = session['comset']
    cookie['1'] = comset_form.comset_1.data
    cookie['2'] = comset_form.comset_2.data
    cookie['3'] = comset_form.comset_3.data
    return 0


def generate_global_config(global_config_form):
    cookie = session['global_config']
    cookie['start_spot'],cookie['end_spot'],cookie['spot_step'] = \
        global_config_form.start_spot.data,global_config_form.end_spot.data,global_config_form.spot_step.data
    cookie['slipage'] = global_config_form.slipage.data
    cookie['exec_algo'] = global_config_form.exec_algo.data
    cookie['com_set'] = global_config_form.com_set.data
    cookie['dual_mode'] = global_config_form.dual_mode.data
    cookie['direction'] = global_config_form.direction.data
    cookie['quant'] = global_config_form.quant.data
    cookie['minTTL'] = global_config_form.minTTL.data
    cookie['maxTTL'] = global_config_form.maxTTL.data
    cookie['skip_days'] = global_config_form.skip_days.data
    cookie['day_step'] = global_config_form.day_step.data

    return 0


@auth.context_processor
def inject_var():
    ret = {}
    ret['mode'] = session['mode'] if 'mode' in session else 0
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
        ret['entry_condtion_values'] = [
            session['entry_conditions'][str(i)]
            for i in range(int(session['entry_conditions']['entry_nconds']))
        ]
    if 'exit_conditions' in session:
        ret['exit_conditions'] = session['exit_conditions']
        ret['exit_condtion_values'] = [
            session['exit_conditions'][str(i)]
            for i in range(int(session['exit_conditions']['exit_nconds']))
        ]

    if 'entry_conditions' in session and 'exit_conditions' in session:
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
    if 'show_backtest' in session:
        ret['show_backtest'] = session['show_backtest']
    if 'show_result' in session:
        ret['show_result'] = session['show_result']
    if 'show_error' in session:
        ret['show_error'] = session['show_error']

    ret['future_indicators_tick'] = ','.join(future_indicators_tick)
    ret['future_indicators_min'] = ','.join(future_indicators_min)
    ret['stock_indicators_day'] = ','.join(stock_all_indicators)

    return ret


def check_backtest(cookie):
    if 'verify' in cookie:
        for k, v in cookie['verify'].iteritems():
            if not v:
                return False
        return True
    return False


def init_session(cookie, force_reset=False):
    
    if 'mode' not in cookie:
        cookie['mode'] = 0
    
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
        cookie['entry_conditions']['0'] = ('AND', 11000, 0, 0, 0, -0.1, 0.1,
                                           120, 0, 0, 0, 0)
        cookie['entry_conditions']['1'] = ('AND', 1500, 0, 0, 0, 0, 98, 5, 0, 0,
                                           0, 0)

    if 'exit_conditions' not in cookie or force_reset:
        cookie['exit_conditions'] = {}
        cookie['exit_conditions']['exit_nconds'] = 2
        cookie['exit_conditions']['0'] = ('OR', 1500, 0, 0, 0, 1.99, 'inf', 6,
                                          0, 0, 0, 0)
        cookie['exit_conditions']['1'] = ('OR', 1500, 0, 0, 0, '-inf', 119.0, 4,
                                          0, 0, 0, 0)

    if 'show_tab' not in cookie or force_reset:
        cookie['show_tab'] = ('data',)
        cookie['show_backtest'] = 0

    if 'last_backtest_tstamp' not in cookie:
        cookie['last_backtest_tstamp'] = (get_today(), 0)

    if 'requestID' not in cookie:
        cookie['requestID'] = 0
        cookie['last_request_id'] = -1
        cookie['last_func_name'] = ''
        cookie['pipeline'] = 0

    if 'last_backtest_tstamp' not in cookie:
        cookie['last_backtest_tstamp'] = (-1, -1)

    if ('show_result' not in cookie):
        cookie['show_result'] = 0
    if ('show_error' not in cookie):
        cookie['show_error'] = 0
    
    if 'error_code' not in cookie: 
        cookie['error_code'] = None

    #for upload instruments files
    #     if 'upload_inss_name' not in cookie:
    #         cookie['upload_inss_name'] = None


def get_main_page_arg_dict(*forms):
    args = {}
    args['submit_form'],args['data_form'],args['modify_data_form'],\
            args['comset_form'],args['modify_comset_form'],\
            args['global_config_form'],args['modify_global_config_form'],\
            args['add_entry_rule_form'],args['add_exit_rule_form'] \
        = forms[0],forms[1],forms[2],forms[3],forms[4],forms[5],forms[6],\
            forms[7],forms[8]
    return args


def get_main_page_form_obj():
    mode = session['mode'] if 'mode' else 0
    CommSetForm = comset_forms[mode]
    DataForm = data_forms[mode]
#     data_form.instruments = instruments_forms_fields[mode]
    return ( SubmitForm(),DataForm(),ModifyDataForm(),\
                        CommSetForm(),ModifyComsetForm(),\
                        GlobalConfigForm(),ModifyGlobalConfigForm(),\
                        EntryRuleForm(),ExitRuleForm() )


###---------------------------------------------------------------------------
'''Query Entry Rule Data'''


@login_required
@auth.route('/query_entry_rule_data', methods=['GET', 'POST'])
def query_entry_rule_data():
    global keys
    entry_table_data = []
    nconds = int(session['entry_conditions']['entry_nconds'])
    for i in range(nconds):
        new_condition = dict(zip(keys, session['entry_conditions'][str(i)]))
        new_condition['id'] = i
        entry_table_data.append(new_condition)

#     print 'query_entry_rule_data = ',entry_table_data
    return jsonify(entry_table_data)
'''Update Entry Rule Data'''


@login_required
@auth.route('/update_entry_rule_data', methods=['GET', 'POST'])
def update_entry_rule_data():
    global keys
    indata_json = {
        key: dict(request.form)[key][0]
        for key in dict(request.form)
    }['data']
    indata = unicode2str(json.loads(indata_json))
    session['entry_conditions'] = {}
    session['entry_conditions']['entry_nconds'] = len(indata)
    for i, entry_obj in enumerate(indata):
        #         print i,entry_obj
        session['entry_conditions'][str(i)] = [
            entry_obj[_field] for _field in keys
        ]
    return jsonify(success=1)


###---------------------------------------------------------------------------
'''Query Exit Rule Data'''


@login_required
@auth.route('/query_exit_rule_data', methods=['GET', 'POST'])
def query_exit_rule_data():
    global keys
    exit_table_data = []
    nconds = int(session['exit_conditions']['exit_nconds'])
    for i in range(nconds):
        new_condition = dict(zip(keys, session['exit_conditions'][str(i)]))
        new_condition['id'] = i
        exit_table_data.append(new_condition)

#     print 'query_entry_rule_data = ',exit_table_data
    return jsonify(exit_table_data)
'''Update Entry Rule Data'''


@login_required
@auth.route('/update_exit_rule_data', methods=['GET', 'POST'])
def update_exit_rule_data():
    global keys
    indata_json = {
        key: dict(request.form)[key][0]
        for key in dict(request.form)
    }['data']
    indata = unicode2str(json.loads(indata_json))
    session['exit_conditions'] = {}
    session['exit_conditions']['exit_nconds'] = len(indata)
    for i, exit_obj in enumerate(indata):
        #         print i,exit_obj
        session['exit_conditions'][str(i)] = [
            exit_obj[_field] for _field in keys
        ]
    return jsonify(success=1)


###----------------------------------------------------------------------------
''' show backtest result'''


@login_required
@auth.route('/show_backtest_result', methods=['GET', 'POST'])
def show_backtest_result():
    session['show_result'], session['show_error'] = 1, 0
    return fill()


@login_required
@auth.route('/backtest_result_error', methods=['GET', 'POST'])
def backtest_result_error():
    error_code = int(request.args.get("error_code"))
    session['error_code'] = error_code
    session['show_error'], session['show_result'] = 1, 0
    return fill()


###----------------------------------------------------------------------------
'''Query BackTest Result '''


@login_required
@auth.route('/query_backtest_result', methods=['GET', 'POST'])
def query_backtest_result():
    if not hasattr(current_user, 'username'):
        return jsonify(result=-1)
    username = current_user.username
    day, tstamp = session['last_backtest_tstamp']
    loginID = '{0}_{1}'.format(day, tstamp)
    pipeline = session['pipeline']
    key = current_app.ipc_api.get_key(day, username, loginID, \
                session['last_request_id'], session['last_func_name'], pipeline)
    if not current_app.ipc_api.exists(key):
        print 'no such key, seems like cppServer no respond or respond later than 1 seconds'
        return jsonify(step = -1,status = -1)
    value = current_app.ipc_api.get_value(key)
    print 'get backtest result query! retValue = ', value['ret']
    if value is not None:
        session['show_backtest'] = 1
        if pipeline == 0:
            if int(value['ret']) >= 0:
                return jsonify(step = 0,status = 0)
            else:
                return jsonify(step = 0,status =-1)
        else:
            for k, v in value['ret'].iteritems():
                if int(v) < 0:
                    return jsonify(step = int(k),status = -1)
            return jsonify(step = len(value['ret']),status = 0)
    else:
        return jsonify(step = -1,status = -1)


###----------------------------------------------------------------------------
''' For log in '''


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            #             login_user(user, form.remember_me.data)
            login_user(user, False)
            init_session(session)
            return redirect(url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


###---------------------------------------------------------------------------
''' for backTest'''


@login_required
@auth.route('/backtest', methods=['GET', 'POST'])
def backtest():
    main_page_forms = get_main_page_form_obj()
    sub_form = main_page_forms[0]
    min_backtest_gap_seconds = 10

    session['show_tab'] = ()
    if sub_form.submit1.data and sub_form.validate_on_submit():

        now = (get_today(), get_hourminsec())
        if session['last_backtest_tstamp'][0] != -1 and diff_seconds(
                now,
                session['last_backtest_tstamp']) < min_backtest_gap_seconds:
            flash('warning! Min backtest time interval is {0}, take a rest~~'.
                  format(min_backtest_gap_seconds))
            return redirect(url_for('auth.fill'))
        else:
            session['last_backtest_tstamp'] = now
            data_dict = web_datablock_to_server_datablock(session['data_block'])
            comset_dict = web_comset_data_to_server_data(session['comset'])
            global_config = web_global_config_to_server_global_config(session['global_config'])
            entry_rules = web_conditions_to_server_conditions_entry(\
                                session['entry_conditions'],session['global_config']['direction'],session['global_config']['quant'])
            exit_rules  = web_conditions_to_server_conditions_exit(\
                                session['exit_conditions'],session['global_config']['minTTL'],session['global_config']['maxTTL'])

            #             print 'data_block = ',data_dict
            #             print 'comset = ',comset_dict
            #             print 'global_config = ',global_config
            #             print 'entry_rules = ',entry_rules
            #             print 'exit_rules = ',exit_rules

            funcNames = ['config_data','create_shm','create_backtest_config',\
                            'backtest','create_pta','upload_pta']
            username = current_user.username

            requestID = session['requestID']
            session['requestID'] += 1

            today, tstamp = now
            loginID = '{0}_{1}'.format(today, tstamp)

            argkws = {}
            argkws['username'], argkws['date'], argkws['tstamp'] = username, today, tstamp

            backtest_pydict = {}
            backtest_pydict['type'] = data_dict['type']
            backtest_pydict['data_block'] = data_dict
            backtest_pydict['comset_data'] = comset_dict
            backtest_pydict['config_data'] = global_config
            backtest_pydict['entry_data'] = entry_rules
            backtest_pydict['exit_data'] = exit_rules
            
            backtest_pydict.update(argkws)

            os.makedirs(get_server_result_path(argkws))

            paras = [data_dict, {}, backtest_pydict, argkws, argkws, argkws]
            pipeline = 1
            paras_dict = dict(
                zip(map(lambda x: str(x), range(len(paras))), paras))
            #             print paras_dict
            session['last_request_id'] = requestID
            session['last_func_name'] = funcNames
            session['pipeline'] = pipeline

            cmd = current_app.rpc_client.create_cmd(today, username, loginID, requestID, funcNames, \
                                                        pipeline, **paras_dict)
            print 'send cmd = ', cmd, '\n'
            current_app.rpc_client.send_cmd(cmd)

            flash('Start back Testing, please wait for a while...')

    args = get_main_page_arg_dict(*main_page_forms)
    args['start_timer'] = 1
    session['show_result'], session['show_error'] = 0, 0
    return render_template('auth/fill.html', **args)


###----------------------------------------------------------------------------
''' For basic UI '''

@login_required
@auth.route('/backtest_mode', methods=['GET'])
def backtest_mode():
    try:
        mode = int(request.args.get("mode"))
    except:
        mode = 0
    #for stock default conditions    
    if mode == 2:
        session['entry_conditions'] = {}
        session['entry_conditions']['entry_nconds'] = 1
        session['entry_conditions']['0'] = ('AND', 11000, 0, 0, 0, -0.1, 0.1, 1, 0, 0, 0, 0)
        session['exit_conditions'] = {}
        session['exit_conditions']['exit_nconds'] = 1
        session['exit_conditions']['0'] = ('OR', 1500, 0, 0, 0, 1.99, 'inf', 6, 0, 0, 0, 0)
        
    session['mode'] = mode
#     print 'mode = ',mode
    return redirect(url_for('auth.fill')) 

@login_required
@auth.route('/fill', methods=['GET', 'POST'])
def fill():
    main_page_forms = get_main_page_form_obj()

    if check_backtest(session) is True:
        session['show_tab'] = ()

#     print 'show session result & error = ',session['show_result'],session['show_error']
    result_args = {}
    if int(session['show_result']) == 1:
        argkws = {}
        argkws['username'],argkws['date'],argkws['tstamp'] = current_user.username,\
            str(session['last_backtest_tstamp'][0]),str(session['last_backtest_tstamp'][1])
        root_dir = get_server_result_path(argkws)

        if os.path.exists(root_dir):
            #1.get summary values
            summary_path = os.path.join(root_dir, 'output.txt')
            summary_values = get_summarys(summary_path)
            summary_values = map(lambda x: x.strip(),
                                 filter(lambda x: len(x.strip()) > 0,
                                        summary_values.strip().split('|')))
            summary_values.pop(1)
            result_args['summary_values'] = summary_values

            #2.get everyday performace
            all = output_parser(summary_path)
            everyday = all[2][3:-1]
            everyday_performace_values = map(lambda x: map(lambda z: z.strip(),filter(lambda y: len(y.strip())>0,x.split('|')) ),everyday)
            result_args[
                'everyday_performace_values'] = everyday_performace_values

            #3.get charts paths
            base_path = r'/static/upload_results'
            base_path = os.path.join(base_path, argkws['username'],
                                     argkws['date'], argkws['tstamp'], 'pta')
            result_args['pnl_path'] = os.path.join(base_path, "pnl.png")
            result_args['position_path'] = os.path.join(base_path,
                                                        "position.png")
            result_args['volatility_path'] = os.path.join(
                base_path, "volatility.png")

            #4.get file addr
            base_path = r'/static/upload_results'
            base_path = os.path.join(base_path, argkws['username'],
                                     argkws['date'], argkws['tstamp'])
            result_args['exit_list'] = os.path.join(
                base_path, "{0}_exit_list.csv".format(current_user.username))
            result_args['summary'] = os.path.join(
                base_path,
                "{0}_total_summary.csv".format(current_user.username))
            result_args['backtest_log'] = os.path.join(
                base_path,
                "output.txt")
        else:
            session['show_error'] = 1
            session['show_result'] = 0

    if int(session['show_error']) == 1:
        argkws = {}
        argkws['username'],argkws['date'],argkws['tstamp'] = current_user.username,\
            str(session['last_backtest_tstamp'][0]),str(session['last_backtest_tstamp'][1])
        root_path = get_server_result_path(argkws)
        errors = os.path.join(root_path, 'output.txt')
        #         print errors
        content = []
        if os.path.exists(errors):
#             with open(errors, 'r+') as fin:
#                 for line in fin:
#                     content.append(line)
#             error_html = '<br>'.join(content)
            error_html = ''
            result_args['error_log_path'] = errors
        else:
            if session['error_code'] is not None:
                error_message = error_code_dict[session['error_code']]
            else:
                error_message = 'Please Run Again'
            error_html = '{}'.format(error_message)
        result_args['error_html'] = error_html

    args = get_main_page_arg_dict(*main_page_forms)
    args.update(result_args)
    return render_template('auth/fill.html', **args)


###----------------------------------------------------------------------------
''' For Shm Block Data'''


@login_required
@auth.route('/fill_data', methods=['POST', 'GET'])
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

    args = get_main_page_arg_dict(*main_page_forms)
    return render_template('auth/fill.html', **args)


@login_required
@auth.route('/modify_data', methods=['POST', 'GET'])
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
@auth.route('/fill_comset_data', methods=['POST', 'GET'])
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
    return render_template('auth/fill.html', **args)


@login_required
@auth.route('/modify_comset_data', methods=['POST', 'GET'])
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
@auth.route('/fill_global_config_data', methods=['POST', 'GET'])
def fill_global_config_data():
    main_page_forms = get_main_page_form_obj()
    global_config_form = main_page_forms[5]
    #     print 'fuck! ',global_config_form.submit6.data
    #     print 'You! ',global_config_form.is_submitted(),global_config_form.validate()
    session['show_tab'] = ('global_config',)
    if global_config_form.submit6.data and global_config_form.validate_on_submit(
    ):
        flash('Set Global Config')
        if generate_global_config(global_config_form) == 0:
            session['verify']['global_config'] = True
        else:
            session['verify']['global_config'] = False
            flash('Please Check Config Parameters Again')
    elif global_config_form.submit6.data and global_config_form.is_submitted(
    ) and not global_config_form.validate():
        flash('Please Check Config Parameters Again')

    args = get_main_page_arg_dict(*main_page_forms)
    return render_template('auth/fill.html', **args)


@login_required
@auth.route('/modify_global_config_data', methods=['POST', 'GET'])
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
@auth.route('/fill_entry_rule_data', methods=['POST', 'GET'])
def fill_entry_rule_data():
    main_page_forms = get_main_page_form_obj()
    rule_form = main_page_forms[7]
    conditions = session['entry_conditions']

    #     print reset_rules.reset_entry_rules.data,reset_rules.is_submitted(),reset_rules.validate()
    #     print rule_form.add_entry_rule.data,rule_form.is_submitted(),rule_form.validate()

    session['show_tab'] = ('entry',)
    if rule_form.add_entry_rule.data and rule_form.validate_on_submit():
        values = ( rule_form.logic.data,rule_form.condID.data,rule_form.flip.data,rule_form.gap.data,rule_form.offset.data,\
                  rule_form.lowthrs.data,rule_form.highthrs.data,\
                   rule_form.para1.data,rule_form.para2.data,rule_form.para3.data,rule_form.para4.data,rule_form.para5.data )
        conditions[str(session['entry_conditions']['entry_nconds'])] = values
        session['entry_conditions']['entry_nconds'] += 1
        flash('add new entry rule')
    elif rule_form.is_submitted() and not rule_form.validate():
        flash('please check the new entry rule again~')

    args = get_main_page_arg_dict(*main_page_forms)
    return render_template('auth/fill.html', **args)


###----------------------------------------------------------------------------
'''for ExitRules'''


@login_required
@auth.route('/fill_exit_rule_data', methods=['POST', 'GET'])
def fill_exit_rule_data():
    main_page_forms = get_main_page_form_obj()
    rule_form = main_page_forms[8]
    conditions = session['exit_conditions']

    #     print reset_rules.reset_exit_rules.data,reset_rules.is_submitted(),reset_rules.validate()
    #     print rule_form.add_exit_rule.data,rule_form.is_submitted(),rule_form.validate()

    session['show_tab'] = ('exit',)
    if rule_form.add_exit_rule.data and rule_form.validate_on_submit():
        values = ( rule_form.logic.data,rule_form.condID.data,rule_form.flip.data,rule_form.gap.data,rule_form.offset.data,\
                  rule_form.lowthrs.data,rule_form.highthrs.data,\
                   rule_form.para1.data,rule_form.para2.data,rule_form.para3.data,rule_form.para4.data,rule_form.para5.data )
        conditions[str(session['exit_conditions']['exit_nconds'])] = values
        session['exit_conditions']['exit_nconds'] += 1
        flash('add new exit rule')
    elif rule_form.is_submitted() and not rule_form.validate():
        flash('please check the new exit rule again~')

    args = get_main_page_arg_dict(*main_page_forms)
    return render_template('auth/fill.html', **args)


###-------------------------------------------------------------------------------
###clear all conditions
@login_required
@auth.route('/reset_all', methods=['POST', 'GET'])
def reset_all():
    init_session(session, force_reset=True)
    session['show_result'], session['show_error'] = 0, 0
    flash('All parameters have been reset!')
    return redirect(url_for('auth.fill'))
