import flask
from flask import request, jsonify
from data.defaultpfp import defaultprofile
from data import db_session
from data.users import User
from data.guides import Guide

blueprint = flask.Blueprint('guide_api', __name__, template_folder='templates')


@blueprint.route('/api/add_guide', methods=['POST'])
def add_guide():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['owner_id', 'name', 'message']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()

    user = Guide(
        owner_id=request.json['owner_id'],
        title=request.json['name'],
        text=str(request.json['message'])
    )
    if 'images' in request.json and request.json['images'] != ['data:image/png;base64,']:
        user.images = str(request.json['images'])
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})

