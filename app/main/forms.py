from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User
from flask.ext.uploads import UploadSet, IMAGES


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(Form):
    body = PageDownField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')


class CommentForm(Form):
    body = StringField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')


images = UploadSet('image', IMAGES)
class UploadTopicForm(Form):
    title = StringField('标题', validators=[Required()])
    content = StringField('内容简介', validators=[Required()])
    image = FileField('封面图', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], '只允许上传图片!')
    ])
    submit = SubmitField('上传')


class UploadVedioForm(Form):
    title = StringField('标题', validators=[Required()])
    image = FileField('封面图', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], '只允许上传图片!')
    ])
    cover_image = FileField('特色封面图', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], '只允许上传图片!')
    ])
    video = FileField('选择视频', validators=[FileRequired()])
    category = SelectField(
        '选择分类',
        choices=[('gdmu', '今日广医'), ('life', '生活娱乐'), ('technology', '科技'), ('movie', '电影'), ('animation', '动漫'), ('tv', '电视剧')]
    )
    submit = SubmitField('上传')