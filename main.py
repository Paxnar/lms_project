import base64
import io
import PIL.Image as Image

from flask import Flask, render_template, redirect, request, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from requests import post, get
from werkzeug.exceptions import abort
from data.defaultpfp import defaultprofile
from data.users import User
from data.profiles import ProfileImage
from data import db_session
from api import user_api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(_):
    return make_response('<h1>error: Not found</h1>', 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lms_html/user/login.html')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == request.form['email']).first()
        if user and user.check_password(request.form['pasw']):
            login_user(user, remember=True)
            return redirect('/')
        return render_template('lms_html/user/login.html', message='Неправильный логин или пароль!')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lms_html/user/signup.html')
    elif request.method == 'POST':
        if request.form['pasw'] != request.form['paswag']:
            return render_template('lms_html/user/signup.html', message='Пароли не совпадают')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == request.form['email']).first():
            return render_template('lms_html/user/signup.html', message="Такой пользователь уже есть!")
        post('http://localhost:5000/api/user',
             json={'email': request.form['email'], 'name': request.form['username'],
                   'password': request.form['pasw']}).json()
        return redirect("/login")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/images/profiles/<id>')
def load_profile(id):
    db_sess = db_session.create_session()
    image = db_sess.query(ProfileImage).filter(ProfileImage.id == id).first()

    return '''<html><head></head><body style="background: gray;"><img src="data:image/png;base64,''' + \
           f'''{base64.b64encode(image.data).decode()}"></body></html>'''


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        image = db_sess.query(ProfileImage).filter(ProfileImage.id == current_user.profile_image).first()
        return render_template("lms_html/index.html", pfp=base64.b64encode(image.data).decode())
    return render_template("lms_html/index.html")


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not current_user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':
        db_sess = db_session.create_session()
        image = db_sess.query(ProfileImage).filter(ProfileImage.id == current_user.profile_image).first()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        return render_template('lms_html/profile/profile.html',
                               pfp='data:image/png;base64,' + base64.b64encode(image.data).decode(), form=user.to_dict(
                only=('email', 'name', 'surname', 'phone', 'country', 'language')))
    elif request.method == 'POST':
        if 'pfpupload' in request.form:
            pfp = request.files['pfpimg'].stream.read()
            if pfp != b'':
                db_sess = db_session.create_session()
                pi = ProfileImage(data=pfp)
                db_sess.add(pi)
                usr = db_sess.query(User).filter(User.id == current_user.id).first()
                usr.profile_image = pi.id
                db_sess.add(usr)
                db_sess.commit()
                post('http://localhost:5000/api/user_edit',
                     json={'user': current_user.id, 'profile_image': pi.id}).json()
                image = db_sess.query(ProfileImage).filter(ProfileImage.id == pi.id).first()
                user = db_sess.query(User).filter(User.id == current_user.id).first()
                return render_template('lms_html/profile/profile.html',
                                       pfp='data:image/png;base64,' + base64.b64encode(image.data).decode(), form=user.to_dict(
                        only=('email', 'name', 'surname', 'phone', 'country', 'language')))
        jsons = {'user': current_user.id}
        for i in request.form:
            if request.form[i] == '' and (i == 'name' or i == 'email'):
                continue
            jsons[i] = request.form[i]
        post('http://localhost:5000/api/user_edit',
             json=jsons).json()
        return redirect("/")


def main():
    db_session.global_init("db/users.db")
    app.register_blueprint(user_api.blueprint)
    db_sess = db_session.create_session()
    image = db_sess.query(ProfileImage).filter(ProfileImage.id == 1).first()
    if not image:
        profileimage = ProfileImage(data=defaultprofile)
        db_sess.add(profileimage)
        db_sess.commit()
    app.run()


if __name__ == '__main__':
    main()
