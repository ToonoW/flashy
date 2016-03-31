from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from . import api
from .decorators import permission_required
from .errors import forbidden
from ..models import Topic


@api.route('/topic/new/')
def get_topic():
    topics = Topic.query.order_by('id').limit(5).all()
    return jsonify({'topics': [topic.to_json() for topic in topics]})
