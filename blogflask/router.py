from flask import render_template, flash, redirect, url_for,request
from blogflask import app
from blogflask.forms import *
from blogflask import db, bcrypt
from blogflask.models import User
from flask_login import login_user, current_user, logout_user, login_required

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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.passwords, form.password.data):
                login_user(user, remember=form.remember.data)
                flash('You have been logged in!', 'success')
                next_page=request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash(' Incorrect username and password', 'danger')
        else:
            flash(' Incorrect username and password', 'danger')


    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, passwords=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'{form.username.data} your account has been created', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account')
@login_required
def account():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',image_file=image_file)


@app.route('/update')
@login_required
def account_update():
    if current_user.is_authenticated:
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=current_user.email)

            db.session.add(user)
            db.session.commit()
            flash(f'{form.username.data} your account has been created', 'success')
    return url_for('account')
