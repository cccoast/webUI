from flask import render_template,request,url_for,flash,redirect,jsonify
from . import main
from .. import ufile
from .forms import UploadForm

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

