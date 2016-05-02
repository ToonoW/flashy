from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Post, Permission
from . import api
from .decorators import permission_required
from .errors import forbidden
import os, time, hashlib

@api.route('/posts/')
def get_posts():
    """推荐的接口"""
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.play_times.desc()).paginate(
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


@api.route('/posts/query/<category>/<int:page>')
def get_posts_by_query(category, page=1):
    """选择按照播放次数或者收藏数排序，并且有分类挑选"""
    pagination = Post.query.filter(Post.category == category).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items

    if category == "recommand":
        pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        posts = pagination.items

    return jsonify({
        'videos': [post.to_json() for post in posts],
        'count': pagination.total
    })


@api.route('/posts/homepage/')
def get_homepage_posts():
    """提供app首页所有栏目的视频信息"""
    recommands = Post.query.order_by(Post.play_times.desc()).limit(4).all()
    gdmus = Post.query.filter(Post.category == 'gdmu').order_by(Post.timestamp.desc()).limit(4).all()
    lifes = Post.query.filter(Post.category == 'life').order_by(Post.timestamp.desc()).limit(4).all()
    technologys = Post.query.filter(Post.category == 'technology').order_by(Post.timestamp.desc()).limit(4).all()
    movies = Post.query.filter(Post.category == 'movie').order_by(Post.timestamp.desc()).limit(4).all()
    musics = Post.query.filter(Post.category == 'music').order_by(Post.timestamp.desc()).limit(4).all()
    animations = Post.query.filter(Post.category == 'animation').order_by(Post.timestamp.desc()).limit(4).all()
    tvs = Post.query.filter(Post.category == 'tv').order_by(Post.timestamp.desc()).limit(4).all()

    return jsonify({
        'msg': '这是首页的所有视频信息接口',
        'recommand': [recommand.to_json() for recommand in recommands],
        'gdmu': [gdmu.to_json() for gdmu in gdmus],
        'life': [life.to_json() for life in lifes],
        'music': [music.to_json() for music in musics],
        'technology': [technology.to_json() for technology in technologys],
        'movie': [movie.to_json() for movie in movies],
        'animation': [animation.to_json() for animation in animations],
        'tv': [tv.to_json() for tv in tvs]
    })


@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.filter(Post.id == id).first()
    if post is not None:
        post.play_times+=1
        db.session.commit()

    return jsonify({
        'author': post.author_id,
        'category': post.category,
        'id': post.id,
        'video_url': post.video_url,
        'video_url_mp4': post.video_url_mp4,
        'title': post.title,
        'introduction': post.introduction,
        'favor_num': post.favor_num,
        'play_times': post.play_times
    })


@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id, _external=True)}


@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
            not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    return jsonify(post.to_json())


# 上传视频
@api.route('/video/upload', methods=['POST'])
#@login_required
def video_upload():
    from ..main.forms import UploadVedioForm_forAPI
    form = UploadVedioForm_forAPI()
    if True:
        post = Post(
            title = form.title.data,
            category = form.category.data
        )
        post.author_id = 3
        dirname = form.video.data.filename + (str)(time.time())
        dirname = tran2md5(dirname)
        abspath = os.path.abspath('app/static/video')
        dirpath = os.path.join(abspath, dirname)

        # TODO 更换相对路径
        dirpath = os.path.join(os.getcwd() + '/app/static/video', dirname)
        os.mkdir(dirpath)

        filename = 'picture' + get_extname(form.image.data.filename)
        form.image.data.save(os.path.join(dirpath, filename))
        post.image_url = '/static/video/' + dirname + '/' + filename

        filename = 'cover_image' + get_extname(form.cover_image.data.filename)
        form.cover_image.data.save(os.path.join(dirpath, filename))
        post.cover_image_url = '/static/video/' + dirname + '/' + filename

        filename = 'video' + get_extname(form.video.data.filename)
        form.video.data.save(os.path.join(dirpath, filename))
        if not get_extname(form.video.data.filename) == '.mp4':
            command = 'ffmpeg -i ' + os.path.join(dirpath, filename) + ' ' + os.path.join(dirpath, 'video.mp4')
            os.popen(command)
        post.video_url = '/static/video/' + dirname + '/' + filename
        post.video_url_mp4 = '/static/video/' + dirname + '/video.mp4'

        db.session.add(post)
        db.session.commit()
        from flask import jsonify
        return jsonify({
            'status': 'success',
            'video_url': post.video_url
        })
    return jsonify({
        'status': 'error'
    })


def tran2md5(src):
    m1 = hashlib.md5()
    m1.update(src.encode('utf-8'))
    return m1.hexdigest()


def get_extname(filename):
    (name, ext) = os.path.splitext(filename)
    return ext


# 搜索标题
@api.route('/posts/search/', methods=['POST'])
def video_search():
    body = request.json
    category = body.get('category', 'all')
    keyword = body.get('keyword', None)
    # order可选选项time, play, favor 分别对应时间，播放数，收藏数
    order = body.get('order', 'time')
    if keyword is not None:
        result_list = []
        if category == 'all':
            result_list = Post.query.whoosh_search(keyword).order_by(switch_search_order(order)).all()
        else:
            result_list = Post.query.filter(Post.category==category).whoosh_search(keyword).order_by(switch_search_order(order)).all()
        return jsonify({
            "msg": "search success",
            "status": 1,
            "resultes": [post.to_json() for post in result_list]
        })
    else:
        return jsonify({
            "msg": "search fail",
            "status": 0
        })


# 返回排序设置
def switch_search_order(order):
    if order == "play":
        return Post.play_times.desc()
    if order == "favor":
        return Post.favor_num.desc()

    return Post.timestamp.desc()