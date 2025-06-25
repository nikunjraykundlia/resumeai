"""Shared extensions such as SQLAlchemy instance."""
from flask_sqlalchemy import SQLAlchemy

# Instantiate SQLAlchemy without an app context; app will initialise later

db = SQLAlchemy()
