from flask import jsonify, request, current_app, url_for
from flask.ext.login import current_user, login_required
from .decorators import permission_required
from . import api
from ..models import User, Post, Permission
from .. import db
from .authentication import verify_password


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


@api.route('/user/<int:id>/setavatar/', methods=['POST', 'GET'])
def avatar_upload(id):
    from ..main.forms import UploadAvatarForm_forAPI
    form = UploadAvatarForm_forAPI()
    if request.method == 'GET':
        from flask import render_template
        return render_template('upload_avatar.html', id=id)
    user = User.query.filter(User.id == id).first()
    image = form.image.data
    if user is not None and image is not None:
        # 保存图片，文件名用hash命名
        import os, hashlib
        m1 = hashlib.md5()
        m1.update(user.email.encode('utf-8'))
        (name, ext) = os.path.splitext(form.image.data.filename)
        filename = m1.hexdigest() + ext
        abspath = os.path.abspath('app/static/avatar')
        filepath = os.path.join(abspath, filename)
        image.save(filepath)

        # 写入数据库
        user.avatar_url = '/static/avatar/' + filename
        db.session.commit()

        return jsonify({
            'status': 1,
            'msg': 'upload avatar success',
            'avatar_url': user.avatar_url
        })

    return jsonify({
        'status': 0,
        'msg': 'fail to upload avatar'
    })


@api.route('/user/<int:id>/setbirthday/<int:birthday>')
def set_birthday(id, birthday):
    user = User.query.filter(User.id == id).first()
    if user is not None and birthday>0:
        user.birthday = birthday;
        db.session.commit()

        return jsonify({
            'status': 1,
            'msg': 'set birthday success'
        })

    return jsonify({
        'status': 0,
        'msg': 'please check your data'
    })


@api.route('/follow/<int:id>/<int:id2>')
def follow_user(id, id2):
    current_user = User.query.filter(User.id == id2).first()
    user = User.query.filter(User.id == id).first()
    if user is not None:
        current_user.follow(user)
        return jsonify({
            "status": 1,
            "msg": "follow success"
        })

    return jsonify({
        "status": 0,
        "msg": "follow fail, can't find user"
    })


@api.route('/unfollow/<int:id>/<int:id2>')
def unfollow_user(id, id2):
    current_user = User.query.filter(User.id == id2).first()
    user = User.query.filter(User.id == id).first()
    if user is not None:
        current_user.unfollow(user)
        return jsonify({
            "status": 1,
            "msg": "unfollow success"
        })

    return jsonify({
        "status": 0,
        "msg": "follow fail, can't find user"
    })


# 检查是否处于关注状态
@api.route('/check_follow/<int:id>/<int:id2>')
def check_follow(id, id2):
    current_user = User.query.filter(User.id == id2).first()
    user = User.query.filter(User.id == id).first()
    if user is not None:
        follow_status = current_user.is_following(user)
        return jsonify({
            "status": 1,
            "msg": "check success",
            "result": follow_status
        })

    return jsonify({
        "status": 0,
        "msg": "check fail, can't find user"
    })


# 分页获取关注人列表
@api.route('/followers/<int:id>')
def followers(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        return jsonify({
            'status': 0,
            'msg': "can't find user"
        })
    followeds =  user.followed.all()
    follower = []

    for f in followeds:
        try:
            u = User.query.filter(User.id == f.followed_id).first()
            info_dic = {'id': u.id,
                        'username': u.username,
                        'avatar_url': u.avatar_url,
                        'about_me': u.about_me
                        }
            follower.append(info_dic)
        except:
            pass

    return jsonify({
        'status': 1,
        'msg': 'pull followers list success',
        'results': follower
    })