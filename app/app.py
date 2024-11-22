from flask import Flask, redirect, url_for, render_template, request
from flask_ckeditor import CKEditor
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
import os

# Function to create and configure the Flask app
def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder='templates')
    app.secret_key = os.getenv('FLASK_APP_SECRET_KEY')  # Add a secret key for session management

    # Initialize CKEditor
    ckeditor = CKEditor(app)
    app.config['CKEDITOR_PKG_TYPE'] = 'basic'

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)

    # User class for Flask-Login
    class User(UserMixin):
        def __init__(self, id):
            self.id = id

    # In-memory user storage
    users = {'test': 'password'}  # Replace with your desired username and password

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    # Login route
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if username in users and users[username] == password:
                user = User(username)
                login_user(user)
                return redirect(url_for('core.index'))
        return render_template('login.html')

    # Logout route
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))

    # Protect all routes with login_required decorator
    @app.before_request
    def before_request():
        if request.path != '/login' and request.path != '/logout' and not current_user.is_authenticated:
            return redirect(url_for('login'))

    # Register all blueprints
    from app.blueprints.core.routes import core
    from app.blueprints.ideas.routes import ideas

    app.register_blueprint(core, url_prefix='/')  # Home page
    app.register_blueprint(ideas, url_prefix='/ideas')  # Ideas page

    return app