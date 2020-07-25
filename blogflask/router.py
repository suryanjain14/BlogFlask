from flask import render_template, flash, redirect, url_for
from blogflask import app
from blogflask.forms import *
from blogflask import db,bcrypt
from blogflask.models import User


posts = [
    {
        'author': 'suryan jain',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'hkdashk'
    },
    {
        'author': 'jain suryan',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'kabhi to ki thi'
    }
]


@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html", posts=posts, title='Home')


@app.route("/about")
def about():
    return render_template("about.html", title='about')


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('You have been logged in!', 'success')
        return redirect(url_for('home'))
    else:
        flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,passwords=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'{form.username.data} your account has been created', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

