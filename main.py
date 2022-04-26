import requests.exceptions
from flask import Flask, render_template, redirect, request, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from requests import post
from werkzeug.exceptions import abort
from forms.user import RegisterForm
from data.users import User, LoginForm
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


@app.route('/')
@app.route('/index')
def index():
    return render_template("lms_html/index.html")


@app.route('/profile')
def profile():
    if not current_user.is_authenticated:
        return redirect('/login')
    return render_template('lms_html/profile/profile.html')


def main():
    db_session.global_init("db/users.db")
    app.register_blueprint(user_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()
