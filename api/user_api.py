import flask
from flask import request, jsonify
from data.defaultpfp import defaultprofile
from data import db_session
from data.users import User
from data.profiles import ProfileImage

blueprint = flask.Blueprint('user_api', __name__, template_folder='templates')


'''@blueprint.route('/api/user_get', methods=['GET'])
def get_user():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == request.json['user']).first()
    return jsonify(
        {
            'user':
                user.to_dict(only=('email', 'name', 'surname', 'phone', 'country', 'language'))
        }
    )'''


@blueprint.route('/api/user_edit', methods=['POST'])
def edit_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == request.json['user']).first()
    if 'profile_image' in request.json:
        user.profile_image = request.json['profile_image']
    if 'name' in request.json:
        user.name = request.json['name']
    if 'surname' in request.json:
        user.surname = request.json['surname']
    if 'email' in request.json:
        user.email = request.json['email']
    if 'phone' in request.json:
        user.phone = request.json['phone']
    if 'language' in request.json:
        user.language = request.json['language']
    if 'country' in request.json:
        user.country = request.json['country']
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/user', methods=['POST'])
def register_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['email', 'name', 'password']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()

    user = User(
        email=request.json['email'],
        name=request.json['name']
    )
    user.set_password(request.json['password'])
    user.profile_image = 1
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})

