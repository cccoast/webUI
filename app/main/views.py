from flask import render_template,request,url_for,flash,redirect,jsonify
from . import main
from .. import ufile
from .forms import UploadForm,RuleForm,ResetRules,JsBindBubmit

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/test', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        filename = ufile.save(form.upload_file.data)
        file_url = ufile.url(filename)
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
    print 'request.args = ',request.args,' input = ',input
    return jsonify(result=input + 100)

@main.route('/testJquery', methods=['GET', 'POST'])
def test_jquery():
    return render_template('test/test_jquery.html')

conditions = {}
nconds = 2
conditions[0] = ('AND',11000,0,0,0,'-0.1','0.1',120,0,0,0,0)
conditions[1] = ('AND',1500,0,0,0,0,98,5,0,0,0,0)
#     conditions[1] = {'ID':1,'logic':'AND','condID':1500,'flip':0,'gap':0,'offset':0,'lowthrs':0,'highthrs':98,\
#                      'para1':5,'para2':0,'para3':0,'para4':0,'para5':0}
    
@main.route('/testForm',methods = ['GET','POST'])
def testForm():
    rule_form = RuleForm()
    reset_rules = ResetRules()
    global conditions,nconds
    
    print reset_rules.reset_entry_rules.data,reset_rules.is_submitted(),reset_rules.validate()
    print rule_form.add_rule.data,rule_form.is_submitted(),rule_form.validate()
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
        
    return render_template('test/rule_form.html',rule_form = rule_form,conditions = conditions.values(),reset_rules = reset_rules)

@main.route('/testFormInTable',methods = ['GET','POST'])
def testFormInTable():
    return render_template('test/form_in_table.html')

@main.route('/test_js_bind',methods = ['GET','POST'])
def test_js_bind():
    iform = JsBindBubmit()
    print iform.submit_js.data,iform.is_submitted(),iform.validate()
    if iform.submit_js.data and iform.validate_on_submit():
        print iform.content.data
        flash("{}".format(iform.content.data))
    else:
        flash("please type in data")
    start_timer = 1
    return render_template('test/test_submit_jquery.html',test_form = iform,start_timer = 1)
    