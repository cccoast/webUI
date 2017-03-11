from flask import render_template, redirect, request, url_for, flash, session, g 
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm,SubmitForm

@auth.context_processor
def inject_user():
    if session.has_key('verify'):
        return dict(verify = session['verify'])

def init_session(_session):
    _session['verify'] = {}
    _session['verify']['data'] = True
    _session['verify']['global'] = False
    _session['verify']['entry'] = False
    _session['verify']['exit'] = False
    _session['verify']['set'] = False

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
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

@login_required
@auth.route('/fill',methods = ['GET','POST'])
def fill():
    sub_form = SubmitForm()
    if sub_form.validate_on_submit():
        flash('Ready to back Testing')
        print session['verify']
    return render_template('auth/fill.html',submit_form = sub_form)


