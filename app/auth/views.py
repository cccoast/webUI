from flask import render_template, redirect, request, url_for, flash, session, g 
from flask_login import login_user, logout_user, login_required, current_user,fresh_login_required
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm,SubmitForm,DataForm

@auth.context_processor
def inject_var():
    ret = {}
    if 'verify' in session:
        ret['verify'] = session['verify']
    if 'data_block' in session:
        ret['data_block'] = session['data_block']
    return ret
    
def init_session(cookie):
    
        cookie['verify'] = {}
        cookie['verify']['data'] = False
        cookie['verify']['global'] = False
        cookie['verify']['entry'] = False
        cookie['verify']['exit'] = False
        cookie['verify']['set'] = False
    
        cookie['data_blcok'] = {}
        
        cookie['config_ready'] = False
        
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, False)
            init_session(session)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@fresh_login_required
@auth.route('/fill',methods = ['GET','POST'])
def fill():
    sub_form = SubmitForm()
    data_form = DataForm()
 
    if sub_form.submit1.data and sub_form.validate_on_submit():
        flash('Ready to back Testing')
    
    print session['verify']
    return render_template('auth/fill.html',submit_form = sub_form,data_form = data_form)

@fresh_login_required
@auth.route('/fill_data',methods = ['GET','POST'])
def fill_data():
    sub_form = SubmitForm()
    data_form = DataForm()

    if data_form.submit2.data and data_form.validate_on_submit():
        flash('Ready to Create Data Block')
        session['verify']['data'] = True
    
    return render_template('auth/fill.html',submit_form = sub_form,data_form = data_form)


