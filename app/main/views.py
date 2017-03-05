from flask import render_template,request,url_for,flash,redirect
from . import main
from .forms import SubmitForm

@main.route('/')
def index():
    sub_form = SubmitForm()
    if sub_form.validate_on_submit():
        flash('Ready to back Testing')
        return redirect(request.args.get('next') or url_for('main.index'))
    return render_template('index.html',submit_form = sub_form)
