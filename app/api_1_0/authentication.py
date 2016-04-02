from flask import jsonify, request, g, abort, url_for, current_app
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from ..models import User, AnonymousUser
from . import api
from .. import db
from .errors import unauthorized, forbidden


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})


@api.route('/register/', methods=['POST'])
def register():
    """注册新用户"""
    body = request.json
    username = body.get('username')
    email = body.get('email')
    password = body.get('password')
    if username and email and password:
        if User.query.filter_by(email=email).first():
            return jsonify({
                'status': 3,
                'msg': '邮箱已被占用'
            })
        if User.query.filter_by(username=username).first():
            return jsonify({
                'status': 2,
                'msg': '用户名已被占用'
            })

        user = User(
            username=username,
            email=email,
            password=password
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'status': 0,
            'msg': '注册成功'
        })

    return jsonify({
        'status': 1,
        'msg': '参数不完整，操作失败'
    })


@api.route('/login/', methods=['POST'])
def login():
    """用户登陆"""
    body = request.json
    email = body.get('email')
    password = body.get('password')
    user = User.query.filter_by(email=email).first()
    if user is not None:
        if user.verify_password(password):
            login_user(user, remember=True)
            return jsonify({
                'status': 0,
                'msg': '登陆成功',
                'username': user.username
            })
        else:
            return jsonify({
                'status': 1,
                'msg': '邮箱与密码不匹配'
            })
    else:
        return jsonify({
            'status': 2,
            'msg': '此邮箱未注册'
        })