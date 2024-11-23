from flask import Flask
from flask_ckeditor import CKEditor
from dotenv import load_dotenv
import os

# Function to create and configure the Flask app
def create_app():
    load_dotenv()

    #Create Flask instance
    app = Flask(__name__, template_folder='templates')
    app.secret_key = os.getenv('FLASK_APP_SECRET_KEY')  # Add a secret key for session management

    # Initialize CKEditor
    ckeditor = CKEditor(app)
    app.config['CKEDITOR_PKG_TYPE'] = 'basic'
    app.config['CKEDITOR_HEIGHT'] = 400  # Customize as needed
    app.config['CKEDITOR_LANGUAGE'] = 'en'

    # Initialize NOCO
    app.config['NOCO_DB_BASE_URL'] = os.getenv('NOCO_DB_BASE_URL')
    app.config['NOCO_DB_TABLE_ID'] = os.getenv('NOCO_DB_API_TOKEN')
    app.config['NOCO_DB_MENUS_TABLE_ID'] = os.getenv('NOCO_DB_MENUS_TABLE_ID')
    app.config['NOCO_DB_OWNERS_TABLE_ID'] = os.getenv('NOCO_DB_OWNERS_TABLE_ID')

    #Initialize MINIO
    app.config['MINIO_URL'] = os.getenv('MINIO_URL')
    app.config['MINIO_ACCESS_KEY'] = os.getenv('MINIO_ACCESS_KEY')
    app.config['MINIO_SECRET_KEY'] = os.getenv('MINIO_SECRET_KEY')


    # Initialize CSRF protection
    #csrf = CSRFProtect(app)

    # Register all blueprints
    from app.blueprints.menu.routes import menu
    from app.blueprints.ideas.routes import ideas

    app.register_blueprint(menu, url_prefix='/')  # Home page
    app.register_blueprint(ideas, url_prefix='/ideas')  # Ideas page

    return app