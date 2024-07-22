"""JSON2Video Flask app"""
import json

# flask
from flask import Flask, render_template, request, url_for, redirect, flash, send_file, jsonify
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

# auth
from flask_login import LoginManager, UserMixin, login_user, \
    logout_user, login_required, current_user
from sqlalchemy.orm import declarative_base, relationship
from werkzeug.security import generate_password_hash, check_password_hash

# json2video
import googleapiclient.errors
from Core.json_parser import JsonParser
from Core.youtube import YoutubeUploader
from Core.form import EditJSONForm

# misc
from os import path, urandom
from datetime import datetime as dt
from uuid import uuid4

# Threading
import threading

# Logging
import logging
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(handlers=[logging.StreamHandler()], encoding='utf-8', level=logging.DEBUG)

# app initialization and config
app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(32)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['JSON_AS_ASCII'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text

engine = create_engine("postgresql+psycopg2://postgres:sna@5.42.81.155:5432/json2video")
connection = engine.connect()

# login manager initialization
login_manager = LoginManager()
login_manager.init_app(app)


class ExportingThread(threading.Thread):
    project_id: str
    render_args: dict[str:str]
    video_file: str
    progress = "0"

    def __init__(self, project_id: str, render_args: dict[str:str]):
        self.progress = "0"
        self.project_id = project_id
        self.render_args = render_args
        self.video_file = ""
        super().__init__()

    def run(self):
        # Your exporting stuff goes here ...
        try:
            parser = JsonParser()  # instantiate json parser
            parser.progressChangeListener = onProgressChanged
            parser.read_from_file(get_json_dest(self.project_id))  # parse the json file
            self.progress = parser.parse_video(video_id=self.project_id,
                                               quality=self.render_args["quality"],
                                               video_format=self.render_args["format"])
        except Exception as e:
            logger.error(e)
            print(e)
            self.progress = "Error"


exporting_threads: dict[str: ExportingThread] = {}


def onProgressChanged(prog: int, project_id: str):
    global progress
    exporting_threads[project_id].progress = str(prog)


Base = declarative_base()


class Video(Base):
    """Video database model"""

    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    youtube_link = Column(String)
    author_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), default=dt.now())


class User(Base, UserMixin):
    """User database model"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(120), nullable=False)
    videos = relationship('Video', backref='users')
    created_at = Column(DateTime(timezone=True), default=dt.now())

    def set_password(self, password):
        """Sets hashed password given a password"""
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        """Checks whether password is correct using hash"""
        return check_password_hash(self.hashed_password, password)


Base.metadata.create_all(engine)
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()


def get_json_dest(unique_id):
    """Returns path to a json file given its id"""
    return path.join(app.config['UPLOAD_FOLDER'], unique_id + '.json')


@app.route('/', methods=['GET', 'POST'])
def index():
    """Index page view"""
    if request.method == 'POST':
        uploaded_file = request.files['file']  # get uploaded file
        if uploaded_file:
            unique_id = str(uuid4())  # generating a unique name to prevent collisions
            unique_dest = get_json_dest(unique_id)
            uploaded_file.save(unique_dest)  # save json file
            return redirect(url_for('render_screen', id=unique_id))  # redirect to render screen
    return render_template('index.html')


@app.route('/render', methods=['GET', 'POST'])
def render_screen():
    """Render page view which allows choice of quality and video format"""
    project_id = request.args.get('id')  # getting a path to json file
    if request.method == 'POST':
        try:
            logger.info('JSON rendering')
            render_args = request.form.to_dict()  # get render arguments from form
            exporting_threads[project_id] = ExportingThread(project_id, render_args)
            exporting_threads[project_id].start()
        except json.decoder.JSONDecodeError:
            logger.error('JSON format is incorrect')
            flash("JSON cannot be decoded. Check for mistakes")
    return render_template('convert_page.html')


@app.route('/progress/<string:thread_id>')
def progress(thread_id):
    global exporting_threads
    if thread_id not in exporting_threads:
        return "no info"
    return str(exporting_threads[thread_id].progress)


@app.route('/preview', methods=['GET', 'POST'])
def preview_screen():
    """Preview page view with options for editing, downloading and uploading into YouTube"""
    video_file = request.args.get('video_file')
    file_id = video_file.split(".")[0]
    if (file_id in exporting_threads):
        del exporting_threads[file_id]
    preview_video_dest = 'preview/' + video_file  # get path to the video file
    if request.method == 'POST':
        if request.form['select'] == 'edit':
            return redirect(url_for('json_edit', id=video_file.split('.')[0]))
        elif request.form['select'] == 'download':
            return send_file(preview_video_dest, as_attachment=True)
        elif request.form['select'] == 'upload':

            return redirect(url_for('upload_video', video_dest=video_file))

    return render_template('preview_page.html', video_dest=preview_video_dest)


@app.route('/upload', methods=['GET', 'POST'])
def upload_video():
    """Upload page view with video title and description input"""
    video_dest = request.args.get('video_dest')
    preview_video_dest = 'preview/' + video_dest  # get path to the video file
    if request.method == 'POST' and request.form['upload'] == 'upload':
        logger.info('Video uploading')
        title = request.form['title']
        desc = request.form['desc']
        try:
            yt_uploader = YoutubeUploader(client_secrets=path.join('Core', 'client_secrets.json'))
            refresh = '1//0cZBaVH5k14IdCgYIARAAGAwSNwF' \
                      '-L9IrmT7GxTDpfPHBgaJ4j6m7DEggRDAVpAGOes9aQqs3reuEQF_WNMqBiyZMUg3uemIEGBg'
            yt_uploader.authenticate(refresh)
            data = {
                'filepath': preview_video_dest,
                'title': title,
                'description': desc
            }
            link = yt_uploader.upload(data)
        except googleapiclient.errors.ResumableUploadError as err:
            logger.error('Video cannot be uploaded')
            return err
        if current_user.is_authenticated:
            current_video = Video(title=title,
                                  description=desc,
                                  youtube_link=link,
                                  author_id=current_user.id)
            session.add(current_video)
            session.commit()
        logger.info('Uploaded successfully')
        return "success! " + link
    return render_template('upload_page.html', video_dest=preview_video_dest)


@app.route('/edit', methods=['GET', 'POST'])
def json_edit():
    """JSON editor view"""
    logger.info('JSON formatting')
    unique_id = request.args.get('id')
    json_file = get_json_dest(unique_id)
    form = EditJSONForm()
    with open(json_file, mode="r", encoding="utf-8") as file:
        content = file.read()
    content = repr(content).replace('\"', '\\"')[1:-1]
    if form.is_submitted():
        print(form.content.data)
        with open(json_file, mode="w", encoding="utf-8") as file:
            new_data = repr(form.content.data)[1:-1].replace('\\r\\n', '\n')
            file.write(new_data)
        return redirect(url_for('render_screen', id=unique_id))
    return render_template('edit_json.html', form=form, content=content)


@app.route("/media_video/<path:filename>")
def media_video(filename):
    """Utility view for getting a video from a given path"""
    # config_any_dir
    return send_file(filename, as_attachment=False)


@login_manager.user_loader
def load_user(user_id):
    """Login manager user loader implementation"""
    logger.info('User loading')
    return session.query(User).get(user_id)


@app.route('/log-in', methods=['GET', 'POST'])
def login():
    """Login page view"""
    logger.info('User trying to login')
    if request.method == 'POST':
        user = session.query(User).filter(User.email == request.form['email']).first()
        if user and user.check_password(request.form['pwd']):
            # login_user(user, remember=form.remember_me.data)
            login_user(user)
            logger.info('User login successfully')
            return redirect(url_for('index'))
        logger.warning('Invalid credentials during user login')
        flash("Invalid credentials!")
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    """Sign up page view"""
    logger.info('User trying to sign up')
    if request.method == 'POST':
        if request.form['pwd'] != request.form['pwd_confirm']:
            logger.warning('Invalid passwords')
            flash('Passwords do not match!')
            return render_template('registration.html')
        if session.query(User).filter(User.email == request.form['email']).first():
            logger.warning('Invalid email')
            flash('This email is already being used')
            return render_template('registration.html')
        user = User()
        user.username = request.form["username"]
        user.email = request.form["email"]
        user.set_password(request.form["pwd"])
        session.add(user)
        session.commit()
        logger.info('Successful sing up')
        return redirect(url_for('login'))
    return render_template('registration.html')


@app.route('/log-out')
@login_required
def logout():
    """User logging out function"""
    logger.info('User trying to logout')
    logout_user()
    return redirect(request.referrer)


@app.route('/my/', methods=['GET', 'POST'])
@login_required
def user_profile():
    """User profile page view"""
    if request.method == 'POST':
        new_name = request.form["name"]
        if new_name and new_name != current_user.username:
            user = session.query(User).filter(User.id == current_user.id).first()
            user.username = new_name
            session.commit()

    return render_template('profile.html')


@app.route('/my/history/')
@login_required
def user_profile_history():
    """User's history of uploaded videos page view"""
    return render_template('history.html')


@app.route('/contact-us')
def contacts_page():
    """Contacts page view"""
    return render_template('contacts.html')


@app.route('/docs')
def docs_page():
    """Documentation page view"""
    return render_template('documentation_new.html')


@app.route('/templates')
def templates_page():
    """Templates page view"""
    return render_template('templates.html')


class MyAdminView(ModelView):
    """Custom Admin view made inaccessible for everyone"""

    @login_required
    def is_accessible(self):
        return current_user.is_authenticated and current_user.id == 1


admin = Admin(app, name='JSON2Video Admin', template_mode='bootstrap3')
admin.add_view(MyAdminView(Video, session))
admin.add_view(MyAdminView(User, session))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234)
