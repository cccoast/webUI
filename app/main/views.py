from flask import render_template,request,url_for,flash,redirect
from . import main

@main.route('/')
def index():
    return render_template('index.html')
