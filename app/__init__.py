from flask import Flask
from flask_cors import CORS
from .config import Config
from .sources import db, migrate

def register_routes(app):
    ## will put all routes here
    pass
    
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)  # Allow frontend access
    
    register_routes(app)
    
    
    return app