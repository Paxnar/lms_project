import base64
import ast
from flask import Flask, render_template, redirect, request, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from requests import post, get
from werkzeug.exceptions import abort
from data.defaultpfp import defaultprofile
from data.users import User
from data.profiles import ProfileImage
from data.guides import Guide
from data import db_session
from api import user_api, guide_api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(_):
    return make_response('<head><title>Learnfull - '
                         '404 - не найдено</title></head><body><h1>404 - не найдено</h1></body>', 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():
    accepted = ['python', 'html5', 'css3', 'js', 'other']
    pfp = ''
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        image = db_sess.query(ProfileImage).filter(ProfileImage.id == current_user.profile_image).first()
        pfp = base64.b64encode(image.data).decode()
        db_sess.close()
    if len(request.args) == 0:
        return redirect('/?category=python')
    if len(request.args) > 1 or 'category' not in request.args:
        return redirect('/')
    if request.args['category'] not in accepted:
        return redirect('/')
    db_sess = db_session.create_session()
    guides = db_sess.query(Guide).filter(Guide.category == request.args['category']).all()
    guides_list = []
    for guide in guides:
        owner = db_sess.query(User).filter(User.id == guide.owner_id).first()
        owner_pfp = db_sess.query(ProfileImage).filter(ProfileImage.id == owner.profile_image).first()
        guide_dict = {'id': str(guide.id),
                      'title': guide.title,
                      'name': owner.name,
                      'category': [guide.category],
                      'owner_pfp': base64.b64encode(owner_pfp.data).decode()}
        guide_text = ast.literal_eval(guide.text)
        if len(''.join(guide_text)) > 42:
            guide_dict['text'] = ''.join(guide_text)[:42] + '...'
        else:
            guide_dict['text'] = ''.join(guide_text)
        guide_dict['len'] = len(guide_dict['text'])
        if guide.category not in ['other', 'python']:
            guide_dict['category'].append(guide.category.upper())
        else:
            guide_dict['category'].append(guide.category.capitalize())
        if owner.surname:
            guide_dict['surname'] = ' ' + owner.surname
        else:
            guide_dict['surname'] = ''
        if guide.images:
            guide_dict['images'] = ast.literal_eval(guide.images)
        else:
            guide_dict['images'] = []
        guides_list.append(guide_dict)
    return render_template("lms_html/index.html", pfp=pfp, category=request.args['category'], guides=guides_list)


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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not current_user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':
        db_sess = db_session.create_session()
        image = db_sess.query(ProfileImage).filter(ProfileImage.id == current_user.profile_image).first()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        diction = user.to_dict(only=('email', 'name', 'surname', 'phone', 'country', 'language'))
        for i in diction:
            if diction[i] is None:
                diction[i] = ''
        return render_template('lms_html/profile/profile.html',
                               pfp='data:image/png;base64,' + base64.b64encode(image.data).decode(), form=diction)
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
                                       pfp='data:image/png;base64,' + base64.b64encode(image.data).decode(),
                                       form=user.to_dict(
                                           only=('email', 'name', 'surname', 'phone', 'country', 'language')))
        jsons = {'user': current_user.id}
        for i in request.form:
            if request.form[i] == '' and (i == 'name' or i == 'email'):
                continue
            jsons[i] = request.form[i]
        post('http://localhost:5000/api/user_edit',
             json=jsons).json()
        return redirect("/")


@app.route('/images/profiles/<id>')
def load_profile(id):
    db_sess = db_session.create_session()
    image = db_sess.query(ProfileImage).filter(ProfileImage.id == id).first()
    if not image:
        return abort(404)

    return '''<html><head></head><body style="background: gray;"><img src="data:image/png;base64,''' + \
           f'''{base64.b64encode(image.data).decode()}"></body></html>'''


@app.route('/create_guide')
def create_guide():
    if not current_user.is_authenticated:
        return redirect('/login')
    return render_template('lms_html/les_form/les_form.html')


@app.route('/guide_preview', methods=['GET', 'POST'])
def guide_preview():
    if not current_user.is_authenticated:
        return redirect('/login')
    if request.method == 'POST':
        if 'stuff' in request.form:
            posting = post('http://localhost:5000/api/add_guide', json=ast.literal_eval(request.form['stuff']))
            return redirect('/guide/' + str(posting.json()['id']))
        images = ['data:image/png;base64,' + base64.b64encode(image.stream.read()).decode() for image in
                  request.files.getlist('attach')]
        form = {'message': request.form['message'].split('\n'),
                'images': images,
                'name': request.form['name'],
                'owner_id': current_user.id,
                'category': request.form['category']}
        form['len'] = len(form['message'])
        return render_template('lms_html/les_form/guide_preview.html', form=form, form_s=str(form))
    return redirect('/create_guide')


@app.route('/guide/<id>')
def guide_view(id):
    getting = get('http://localhost:5000/api/get_guide/' + id)
    if getting.text == 'not found':
        return abort(404)
    return render_template('lms_html/les_form/guide.html', form=getting.json())


def main():
    db_session.global_init("db/users.db")
    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(guide_api.blueprint)
    db_sess = db_session.create_session()
    image = db_sess.query(ProfileImage).filter(ProfileImage.id == 1).first()
    if not image:
        profileimage = ProfileImage(data=defaultprofile)
        db_sess.add(profileimage)
        db_sess.commit()
    app.run()


if __name__ == '__main__':
    main()
