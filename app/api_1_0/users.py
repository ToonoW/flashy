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


@api.route('/user/<int:id>/setusername/', methods=['POST'])
def set_username(id):
    body = request.json
    username = body.get('username')
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


@api.route('/user/<int:id>/setaboutme/', methods=['POST'])
def set_aboutme(id):
    body = request.json
    about_me = body.get('about_me')
    user = User.query.filter(User.id == id).first()
    if user is not None and about_me is not None:
        user.about_me = about_me
        db.session.commit()
        return jsonify({
            'status': 1,
            'msg': 'modified success'
        })
    return jsonify({
        'status': 0,
        'msg': 'please check your data'
    })