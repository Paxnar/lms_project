from flask import Flask, render_template, redirect, request, jsonify, make_response, url_for
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
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        post('http://localhost:5000/api/user',
             json={'email': form.email.data, 'name': form.name.data, 'password': form.password.data}).json()
        return redirect('/login')
    return render_template('register.html', title='Регистрация',
                           form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
@app.route('/index')
def index():
    if request.args.get('language') is None:
        return render_template("base.html", title='LMS', language='ru')
    return render_template("base.html", title='LMS', language=request.args.get('language'))
    '''db_sess = db_session.create_session()
    news = db_sess.query(Jobs).all()
    return render_template("index.html", news=news)'''


@app.route('/language')
def change_language():
    if request.args.get('language') == 'ru':
        language = 'en'
    else:
        language = 'ru'
    return redirect(f'/?language={language}')


def main():
    db_session.global_init("db/users.db")
    app.register_blueprint(user_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()
