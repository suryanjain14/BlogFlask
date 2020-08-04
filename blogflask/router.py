from flask import render_template, flash, redirect, url_for, request
from blogflask import app
from blogflask.forms import *
from blogflask import db, bcrypt
from blogflask.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
import secrets
import os


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("home.html", posts=posts, title='Home', user=User())

@app.route('/posts/<user_id>')
def user_posts(user_id):
    user = User.query.get(user_id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("user_posts.html", posts=posts, title=current_user.username + ' Posts', user=user)


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
                next_page = request.args.get('next')
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


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    i = Image.open(form_picture)
    i.thumbnail((125, 125))
    i.save(picture_path)
    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
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
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_posts():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, user_id=current_user.id, content=form.content.data)
        db.session.add(post)
        db.session.commit()
        flash(f'{current_user.username} Content Posted', 'success')
        return redirect(url_for('new_posts'))
    return render_template('create_post.html', title='Posts', form=form)





@app.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
def post_edit(post_id):
    post = Post.query.get(post_id)
    try:
        if post.user_id == current_user.id:
            form = PostEdit()
            if form.validate_on_submit():
                post.title = form.title.data
                post.content = form.content.data
                db.session.commit()

                flash(f'{post.title} has been updated', 'success')
                return redirect(url_for('user_posts', user_id=current_user.id))
            elif request.method == 'GET':
                form.title.data = post.title
                form.content.data = post.content
            return render_template("edit_post.html", post=post, form=form)
        else:
            return redirect(url_for('home'))
    except:
        flash(f'ACCESS DENIED', 'danger')
        return redirect(url_for('home'))


@app.route('/post/delete/<int:post_id>')
def delete_post(post_id):
    post = Post.query.get(post_id)
    try:
        if post.user_id == current_user.id:
            db.session.delete(post)
            db.session.commit()
            return redirect(url_for('user_posts', user_id=current_user.id))
        else:
            return redirect(url_for('home'))
    except:
        flash(f'ACCESS DENIED', 'danger')
        return redirect(url_for('home'))
