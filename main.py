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
        return render_template('login.html')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == request.form['email']).first()
        if user and user.check_password(request.form['pasw']):
            return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        post('http://localhost:5000/api/user',
             json={'email': request.form['email'], 'name': request.form['username'], 'password': request.form['pasw']}).json()
        return redirect("/")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
@app.route('/index')
def index():
    return render_template("base.html")
    '''db_sess = db_session.create_session()
    news = db_sess.query(Jobs).all()
    return render_template("index.html", news=news)'''


def main():
    db_session.global_init("db/users.db")
    app.register_blueprint(user_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()
