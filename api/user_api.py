import flask
from flask import request, jsonify

from data import db_session
from data.users import User

blueprint = flask.Blueprint('user_api', __name__, template_folder='templates')


'''@blueprint.route('/api/jobs')
def get_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return jsonify(
        {
            'jobs':
                [item.to_dict(only=('id', 'team_leader', 'job', 'work_size', 'collaborators', 'start_date', 'end_date',
                                    'is_finished'))
                 for item in jobs]
        }
    )'''


'''@blueprint.route('/api/jobs/<int:jobs_id>', methods=['GET'])
def get_one_jobs(jobs_id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).get(jobs_id)
    if not jobs:
        return jsonify({'error': 'Not found'})
    return jsonify({'jobs': jobs.to_dict(only=('id', 'team_leader', 'job', 'work_size', 'collaborators', 'start_date',
                                               'end_date', 'is_finished'))})'''


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
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})

