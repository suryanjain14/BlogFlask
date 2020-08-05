from flask import Blueprint
from flask import render_template, flash, redirect, request
from flask_login import login_user, logout_user, login_required
from blogflask import db, bcrypt
from blogflask.models import Post
from blogflask.users.forms import *
from blogflask.users.utils import *


users = Blueprint('users', __name__)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.passwords, form.password.data):
                login_user(user, remember=form.remember.data)
                flash('You have been logged in!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash(' Incorrect username and password', 'danger')
        else:
            flash(' Incorrect username and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, passwords=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'{form.username.data} your account has been created', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    form = AccountUpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f'{form.username.data} your account has been updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('verification email sent', 'info')

    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Token expired or invalid Token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.passwords = hashed_password
        db.session.commit()
        flash(f'{user.username}your password has been reset', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset password', form=form)


@users.route('/posts/<user_id>')
def user_posts(user_id):
    user = User.query.get(user_id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("user_posts.html", posts=posts, title=current_user.username + ' Posts', user=user)
