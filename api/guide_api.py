import ast
import flask
from flask import request, jsonify
from data.defaultpfp import defaultprofile
from data import db_session
from data.users import User
from data.guides import Guide

blueprint = flask.Blueprint('guide_api', __name__, template_folder='templates')


@blueprint.route('/api/get_guide/<id>')
def get_guide(id):
    db_sess = db_session.create_session()
    guide = db_sess.query(Guide).filter(Guide.id == id).first()
    if not guide:
        return 'not found'
    else:
        user = db_sess.query(User).filter(User.id == guide.owner_id).first()
        form = {'owner': user.name,
                'name': guide.title,
                'message': ast.literal_eval(guide.text)}
        form['len'] = len(form['message'])
        if guide.images:
            form['images'] = ast.literal_eval(guide.images)
        if user.surname:
            form['owner'] += ' ' + user.surname
        return jsonify(form)


@blueprint.route('/api/add_guide', methods=['POST'])
def add_guide():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['owner_id', 'name', 'message', 'category']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()

    guide = Guide(
        owner_id=request.json['owner_id'],
        title=request.json['name'],
        text=str(request.json['message']),
        category=request.json['category']
    )
    if 'images' in request.json and request.json['images'] != ['data:image/png;base64,']:
        guide.images = str(request.json['images'])
    db_sess.add(guide)
    db_sess.commit()
    return jsonify({'success': 'OK', 'id': guide.id})
