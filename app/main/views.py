from flask import render_template, request, url_for, flash, redirect, jsonify
from . import main
from .. import ufile
from .forms import UploadForm, RuleForm, ResetRules, JsBindBubmit, RadioBoxForm
import os
import json

import sys
upper_abs_path = os.path.sep.join(
    (os.path.abspath(os.curdir).split(os.path.sep)[:-1]))
pkg_path = os.path.join(upper_abs_path, 'generate_data_block')
# print pkg_path
if pkg_path not in sys.path:
    sys.path.append(pkg_path)

from transfer import get_server_result_path
from pta import get_summarys
from pta import parser as output_parser
from misc import unicode2str
from data_center_config import future_indicators_tick, future_indicators_min


@main.route('/')
def index():
    return render_template('index.html')


#----------------------------------------------------------------
#@The below code are all testing code
@main.route('/test', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        filename = ufile.save(form.upload_file.data)
        file_url = ufile.url(filename)
        print file_url
    else:
        file_url = None
    return render_template('test/upload.html', form=form, file_url=file_url)


@main.route('/progressbar', methods=['GET', 'POST'])
def progressbar():
    return render_template('test/progressbar.html')


initV = 0


@main.route('/getValue', methods=['GET', 'POST'])
def getValue():
    global initV
    initV = initV + 5 if (initV <= 95) else 0
    return jsonify(result=initV)


@main.route('/square', methods=['GET', 'POST'])
def square():
    input = request.args.get('value', -1, type=int)
    print 'request.args = ', request.args, ' input = ', input
    return jsonify(result=input + 100)


@main.route('/testJquery', methods=['GET', 'POST'])
def test_jquery():
    return render_template('test/test_jquery.html')


conditions = {}
nconds = 2
conditions[0] = ('AND', 11000, 0, 0, 0, '-0.1', '0.1', 120, 0, 0, 0, 0)
conditions[1] = ('AND', 1500, 0, 0, 0, 0, 98, 5, 0, 0, 0, 0)
#     conditions[1] = {'ID':1,'logic':'AND','condID':1500,'flip':0,'gap':0,'offset':0,'lowthrs':0,'highthrs':98,\
#                      'para1':5,'para2':0,'para3':0,'para4':0,'para5':0}


@main.route('/testForm', methods=['GET', 'POST'])
def testForm():
    rule_form = RuleForm()
    reset_rules = ResetRules()
    global conditions, nconds

    print reset_rules.reset_entry_rules.data, reset_rules.is_submitted(
    ), reset_rules.validate()
    print rule_form.add_rule.data, rule_form.is_submitted(), rule_form.validate(
    )
    if reset_rules.reset_entry_rules.data and reset_rules.validate_on_submit():
        flash('reset_all_rules')
        conditions = {}
        nconds = 0
    elif rule_form.add_rule.data and rule_form.validate_on_submit():
        values = ( rule_form.logic.data,rule_form.condID.data,rule_form.flip.data,rule_form.gap.data,rule_form.offset.data,\
                  rule_form.lowthrs.data,rule_form.highthrs.data,\
                   rule_form.para1.data,rule_form.para2.data,rule_form.para3.data,rule_form.para4.data,rule_form.para5.data )
        conditions[nconds] = values
        nconds += 1
        flash('add new condition')
    elif rule_form.is_submitted() and not rule_form.validate():
        flash('please check the new rule again')

    return render_template(
        'test/rule_form.html',
        rule_form=rule_form,
        conditions=conditions.values(),
        reset_rules=reset_rules)


@main.route('/testFormInTable', methods=['GET', 'POST'])
def testFormInTable():
    return render_template('test/form_in_table.html')


@main.route('/test_js_bind', methods=['GET', 'POST'])
def test_js_bind():
    iform = JsBindBubmit()
    print iform.submit_js.data, iform.is_submitted(), iform.validate()
    if iform.submit_js.data and iform.validate_on_submit():
        print iform.content.data
        flash("{}".format(iform.content.data))
    else:
        flash("please type in data")
    start_timer = 1
    return render_template(
        'test/test_submit_jquery.html', test_form=iform, start_timer=1)


@main.route('/show_charts_and_text', methods=['GET', 'POST'])
def show_charts_and_text():

    base_path = r'/static/upload_results/xudi/20170515/114047/pta'
    username, date, tstamp = 'xudi', str(20170515), str(114047)
    pnl_path = os.path.join(base_path, "pnl.png")
    position_path = os.path.join(base_path, "position.png")
    volatility_path = os.path.join(base_path, "volatility.png")
    print pnl_path, position_path, volatility_path
    base_path = r'/static/upload_results'
    base_path = os.path.join(base_path, username, date, tstamp)
    exit_list = os.path.join(base_path, "{0}_exit_list.csv".format(username))
    summary = os.path.join(base_path, "{0}_total_summary.csv".format(username))
    print exit_list, summary
    root_path = r'/media/xudi/coding/Users/user/workspace/webUI/app/static/upload_results'
    errors = os.path.join(root_path, username, date, tstamp, 'output.txt')
    print errors
    content = []
    with open(errors, 'r+') as fin:
        for line in fin:
            content.append(line)
    error_html = '<br>'.join(content)
    return render_template('test/show_charts_and_text.html',pnl_path = pnl_path,\
                                        position_path = position_path,volatility_path = volatility_path,\
                                        exit_list = exit_list,summary = summary,error_html = error_html)


@main.route('/test_backtest_result', methods=['GET', 'POST'])
def test_backtest_result():
    argkws = {}
    result_args = {}
    username = "xudi"
    argkws['username'], argkws['date'], argkws['tstamp'] = username, str(
        20170515), str(114047)
    root_dir = get_server_result_path(argkws)
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
    result_args['everyday_performace_values'] = everyday_performace_values

    #3.get charts paths
    base_path = r'/static/upload_results'
    base_path = os.path.join(base_path, argkws['username'], argkws['date'],
                             argkws['tstamp'], 'pta')
    result_args['pnl_path'] = os.path.join(base_path, "pnl.png")
    result_args['position_path'] = os.path.join(base_path, "position.png")
    result_args['volatility_path'] = os.path.join(base_path, "volatility.png")

    #4.get file addr
    base_path = r'/static/upload_results'
    base_path = os.path.join(base_path, argkws['username'], argkws['date'],
                             argkws['tstamp'])
    result_args['exit_list'] = os.path.join(
        base_path, "{0}_exit_list.csv".format(username))
    result_args['summary'] = os.path.join(
        base_path, "{0}_total_summary.csv".format(username))
    result_args['show_result'] = 1
    return render_template('test/test_backtest_result.html', **result_args)


@main.route('/test_error_result', methods=['GET', 'POST'])
def test_error_result():
    argkws = {}
    result_args = {}
    username = "xudi"
    argkws['username'], argkws['date'], argkws['tstamp'] = username, str(
        20170515), str(114047)
    root_path = get_server_result_path(argkws)
    errors = os.path.join(root_path, 'output.txt')
    print errors
    content = []
    with open(errors, 'r+') as fin:
        for line in fin:
            content.append(line)
    error_html = '<br>'.join(content)
    result_args['error_html'] = error_html
    result_args['show_error'] = 1
    return render_template('test/test_backtest_result.html', **result_args)


@main.route('/edit_table_content', methods=['GET', 'POST'])
def edit_table_content():
    content_dict = [{
        'id': 1,
        'name': 'Item 1',
        'price': '$1'
    }, {
        'id': 2,
        'name': 'Item 2',
        'price': '$2'
    }, {
        'id': 3,
        'name': 'Item 3',
        'price': '$3'
    }]
    return jsonify(data=content_dict)


@main.route('/update_table_content', methods=['GET', 'POST'])
def refresh_table_content():
    #     try:
    #         print request.get_json(), request.get_json(force=True)
    #     except:
    #         print 'fuck you'
    #     print zip(range(5),(request.form, request.args, request.values, request.data, request.json))
    indata = unicode2str(
        {key: dict(request.form)[key][0]
         for key in dict(request.form)})
    print 'injson = ', indata['data']
    return jsonify(ret='success')


@main.route('/edit_table', methods=['GET', 'POST'])
def edit_table():
    result_args = {}
    return render_template('test/edit_table.html', **result_args)


@main.route('/set_radio_box', methods=['GET', 'POST'])
def set_radio_box():
    radio_form = RadioBoxForm()
    result_args = {'future_indicators_tick':','.join(future_indicators_tick),\
                   'future_indicators_min':','.join(future_indicators_min),\
                   'radio_form':radio_form}
    return render_template('test/jquery_radio_button_set_value.html',
                           **result_args)
