from flask import render_template,request,url_for,flash,redirect,jsonify
from . import main
from .. import ufile
from .forms import UploadForm,TestTableForm

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

@main.route('/testForm',methods = ['GET','POST'])
def testForm():
    test_form = TestTableForm()
    print test_form.submit1.data,test_form.is_submitted(),test_form.validate()
    if test_form.validate_on_submit():
        flash('hello world {0} {1} {2}'.format(test_form.start_spot.data,test_form.end_spot.data,test_form.spot_step.data) )
    return render_template('test/test_form.html',test_form = test_form)
