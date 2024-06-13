from flask import Flask, logging
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from os import path
from werkzeug.security import generate_password_hash
import locale
import os
from flask_cors import CORS
import traceback

# Load environment variables
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

login_manager = LoginManager()
db = SQLAlchemy()

def create_app():
    global app
    app = Flask(__name__)   
    CORS(app)

    try:
        locale.setlocale(locale.LC_TIME, "id_ID")
        logger.debug("Locale set to id_ID")
    except locale.Error as e:
        locale.setlocale(locale.LC_TIME, '')  # Use default locale
        logger.warning(f"Failed to set locale to id_ID: {e}")

    hostname = "b2y.h.filess.io"
    database = "appkulilis_emptybelow"
    port = "3307"
    username = "appkulilis_emptybelow"
    password = "4eb04dd242c9dd3b6beb0248472453e4ee964445"
    
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')
    # app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')
    # app.config['MAX_CONTENT_PATH'] = os.environ.get('MAX_CONTENT_PATH') * 1024 * 1024
    db.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models.user import User, Profile, Time

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(str(id))
    
    # Register blueprints
    from .views.auth.auth import auth
    from .views.user.home import home
    from .views.user.cbf import cbf_algoritma

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(home, url_prefix='/')
    app.register_blueprint(cbf_algoritma, url_prefix='/')

    # ADMIN
    from .views.admin.home import DBhome

    app.register_blueprint(DBhome, url_prefix='/')

    # Register filters
    from .utils import filters

    app.jinja_env.filters['format_date'] = filters.format_date
    app.jinja_env.filters['date_range'] = filters.date_range
    app.jinja_env.filters['enum'] = filters.enum
    app.jinja_env.filters['comma_join'] = filters.comma_join
    app.jinja_env.filters['to_html'] = filters.to_html

    # Register global error handler
    app.register_error_handler(401, lambda error: { 'message': str(error) })
    app.register_error_handler(404, lambda error: { 'message': str(error) })
    app.register_error_handler(500, lambda error: { 'message': str(error) })

    def global_error_handler(error):
        traceback.print_exc()
        return { 'message': str(error) }

    app.register_error_handler(Exception, global_error_handler) 

    with app.app_context():
        db.create_all()
        default_db = User.query.all()
        default_time = Time.query.all()
        if not default_db:
            new_admin = User(username='lilis', password=generate_password_hash('password', method='sha256'), role='admin')
            db.session.add(new_admin)
            db.session.commit()

            new_profile_admin = Profile(name="Lilis", address="Indonesia", photo="", user_id=new_admin.id)
            db.session.add(new_profile_admin)
            db.session.commit()

        if not default_time:
            times = [
                "08.00 s.d 09.00 WIB",
                "09.00 s.d 10.00 WIB",
                "10.00 s.d 11.00 WIB",
                "11.00 s.d 12.00 WIB",
                "13.00 s.d 14.00 WIB",
                "14.00 s.d 15.00 WIB",
                "15.00 s.d 16.00 WIB",
                "16.00 s.d 17.00 WIB",
                "17.00 s.d 18.00 WIB",
                "18.00 s.d 19.00 WIB",
                "19.00 s.d 20.00 WIB",
                "20.00 s.d 21.00 WIB"
            ]
            for time in times:
                new_time = Time(time=time)
                db.session.add(new_time)
                db.session.commit()

    return app
