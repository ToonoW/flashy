from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Post, Permission
from . import api
from .decorators import permission_required
from .errors import forbidden


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
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({
        'videos': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
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
    post = Post.query.get_or_404(id)
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
