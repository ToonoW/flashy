from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User, Post
from .. import db


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/users/<int:id>/timeline/')
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/user/<int:id>/setsex/<string:sex>')
def set_sex(id, sex):
    user = User.query.filter(User.id == id).first()
    if user is not None and (sex in ['male', 'female', 'secret']):
        user.sex = sex
        db.session.commit()
        return jsonify({
            'status': 1,
            'msg': 'modified success'
        })

    return jsonify({
        'status': 0,
        'msg': 'please check your data'
    })


@api.route('/user/<int:id>/setusername/<string:username>')
def set_username(id, username):
    user = User.query.filter(User.id == id).first()
    if user is not None and username is not None:
        user.username = username
        db.session.commit()
        return jsonify({
            'status': 1,
            'msg': 'modified success'
        })
    return jsonify({
        'status': 0,
        'msg': 'please check your data'
    })