from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from blogflask import db
from blogflask.models import Post
from blogflask.posts.forms import *
from flask_login import current_user, login_required


posts = Blueprint('posts', __name__)


@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_posts():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, user_id=current_user.id, content=form.content.data)
        db.session.add(post)
        db.session.commit()
        flash(f'{current_user.username} Content Posted', 'success')
        return redirect(url_for('posts.new_posts'))
    return render_template('create_post.html', title='Posts', form=form)


@posts.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
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
                return redirect(url_for('users.user_posts', user_id=current_user.id))
            elif request.method == 'GET':
                form.title.data = post.title
                form.content.data = post.content
            return render_template("edit_post.html", post=post, form=form)
        else:
            return redirect(url_for('main.home'))
    except AttributeError:
        flash(f'ACCESS DENIED', 'danger')
        return redirect(url_for('main.home'))


@posts.route('/post/delete/<int:post_id>')
def delete_post(post_id):
    post = Post.query.get(post_id)
    try:
        if post.user_id == current_user.id:
            db.session.delete(post)
            db.session.commit()
            return redirect(url_for('users.user_posts', user_id=current_user.id))
        else:
            return redirect(url_for('main.home'))
    except AttributeError:
        flash(f'ACCESS DENIED', 'danger')
        return redirect(url_for('main.home'))
