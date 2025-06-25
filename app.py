import os
from dotenv import load_dotenv
import logging
import re
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from extensions import db
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define base for SQLAlchemy models
class Base(DeclarativeBase):
    pass



# Load env vars
load_dotenv()

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///resume_analyzer.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max

# Custom filters
def nl2br(value):
    """Convert newlines to <br> tags."""
    if not value:
        return ''
    return value.replace('\n', '<br>')

app.jinja_env.filters['nl2br'] = nl2br

# Register a markdown filter
import re
from markupsafe import Markup

def markdown_to_html(text):
    """Simple markdown to HTML converter for improvement suggestions"""
    if not text:
        return ''
    
    # Convert headers
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    
    # Convert lists
    text = re.sub(r'^\* (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^- (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^(\d+)\. (.*?)$', r'<li>\2</li>', text, flags=re.MULTILINE)
    
    # Replace consecutive list items with proper lists
    text = re.sub(r'(<li>.*?</li>)\n(<li>.*?</li>)', r'\1\2', text)
    text = re.sub(r'(<li>.*?</li>)+', r'<ul>\g<0></ul>', text)
    
    # Convert bold and italic
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Convert paragraphs (line breaks)
    text = re.sub(r'\n\n', r'</p><p>', text)
    
    # Wrap in paragraphs if not already wrapped
    if not text.startswith('<'):
        text = f'<p>{text}</p>'
    
    return Markup(text)

app.jinja_env.filters['markdown'] = markdown_to_html

# Number formatting filter
@app.template_filter('format_number')
def format_number(value):
    """Format a number with commas as thousands separators"""
    try:
        return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return value

app.jinja_env.filters['format_number'] = format_number

# Initialize the app with the extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Import routes after app initialization
from routes import register_routes
register_routes(app)

# Import models and create tables
with app.app_context():
    import models
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
