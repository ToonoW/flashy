from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm,\
    CommentForm, UploadTopicForm, UploadVedioForm
from .. import db
from ..models import Permission, Role, User, Post, Comment, Topic, Post
from ..decorators import admin_required, permission_required
import os, time, hashlib


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'

# 主页
@main.route('/', methods=['GET', 'POST'])
def index():
    recommands = Post.query.order_by(Post.play_times.desc()).limit(9).all()
    gdmus = Post.query.filter(Post.category == 'gdmu').order_by(Post.timestamp.desc()).limit(8).all()
    lifes = Post.query.filter(Post.category == 'life').order_by(Post.timestamp.desc()).limit(9).all()
    technologys = Post.query.filter(Post.category == 'technology').order_by(Post.timestamp.desc()).limit(5).all()
    movies = Post.query.filter(Post.category == 'movie').order_by(Post.timestamp.desc()).limit(6).all()
    musics = Post.query.filter(Post.category == 'music').order_by(Post.timestamp.desc()).limit(4).all()
    animations = Post.query.filter(Post.category == 'animation').order_by(Post.timestamp.desc()).limit(5).all()
    tvs = Post.query.filter(Post.category == 'tv').order_by(Post.timestamp.desc()).limit(4).all()

    return render_template('index.html', recommands=recommands, gdmus=gdmus, lifes=lifes, technologys=technologys, movies= movies, musics=musics, animations=animations, tvs=tvs)


# GDMU
@main.route('/gdmu')
def gdmu_category():
    gdmus = Post.query.filter(Post.category == 'gdmu').order_by(Post.timestamp.desc()).limit(9).all()

    return render_template('GDMU.html', gdmus=gdmus)

# tv
@main.route('/tv')
def tv_category():
    tvs = Post.query.filter(Post.category == 'tv').order_by(Post.timestamp.desc()).all()

    return render_template('tv.html', tvs=tvs)

# movie
@main.route('/movie')
def movie_category():
    movies = Post.query.filter(Post.category == 'movie').order_by(Post.timestamp.desc()).all()

    return render_template('tv.html', tvs=movies)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/video/play/<int:id>', methods=['GET', 'POST'])
def play_video(id):
    post = Post.query.get_or_404(id)
    try:
        post.play_times = post.play_times + 1
        db.session.commit()
    except:
        pass
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items

    others = Post.query.filter(Post.category == post.category).order_by(Post.timestamp.desc()).limit(4).all()
    return render_template('play.html', video=post, form=form,
                           comments=comments, pagination=pagination, others=others)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


# 上传topic
@main.route('/topic/upload', methods=['POST', 'GET'])
@login_required
def topic_upload():
    form = UploadTopicForm()
    if form.validate_on_submit():
        topic = Topic(title=form.title.data,
                      content=form.content.data)
        topic.author_id = current_user.id
        form.image.data.save(os.getcwd() + '/app/static/topic_image/' + form.image.data.filename)
        topic.image_url = '/static/topic_image/' + form.image.data.filename

        db.session.add(topic)
        db.session.commit()
        flash("上传新主题成功！")
        return redirect(url_for('.topic_upload'))
    return render_template('upload_topic.html', form=form)


# 上传视频
@main.route('/video/upload', methods=['POST', 'GET'])
@login_required
def video_upload():
    form = UploadVedioForm()
    if form.validate_on_submit():
        post = Post(
            title = form.title.data,
            category = form.category.data
        )
        post.author_id = current_user.id
        dirname = form.video.data.filename + (str)(time.time())
        dirname = tran2md5(dirname)
        abspath = os.path.abspath('app/static/video')
        dirpath = os.path.join(abspath, dirname)

        # TODO 更换相对路径
        dirpath = os.path.join(os.getcwd() + '/app/static/video', dirname)
        os.mkdir(dirpath)

        filename = 'picture' + get_extname(form.image.data.filename)
        form.image.data.save(os.path.join(dirpath, filename))
        from PIL import Image
        im = Image.open(os.path.join(dirpath, filename))
        out = im.resize((263, 147))
        out.save(os.path.join(dirpath, filename))
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
        flash("视频上传成功")
        return redirect(url_for('.video_upload'))
    return render_template('upload_video.html', form=form)


def tran2md5(src):
    m1 = hashlib.md5()
    m1.update(src.encode('utf-8'))
    return m1.hexdigest()


def get_extname(filename):
    (name, ext) = os.path.splitext(filename)
    return ext
