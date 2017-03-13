from flask import render_template,request,url_for,flash,redirect
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
    return render_template('test.html', form=form, file_url=file_url)
