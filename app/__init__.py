from flask import Flask
from flask_cors import CORS
from flask import jsonify


from .config import Config
from .sources import db, migrate
from .routes import auth_bp, projects_bp, tasks_bp, time_entries_bp, teams_bp, users_bp

def register_routes(app: Flask):
    """
    Register all blueprints for the application.
    """
    print("registering routes")
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(time_entries_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(users_bp)
    
    

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    # CORS(app, resources={r"/api/*": {"origins": ["http://localhost:*" ]}})

    CORS(app)  # Allow frontend access
    # CORS(app, resources={r"/*": {"origins": "*"}})
    # CORS(app, supports_credentials=True, allow_headers="*", origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Register routes
    register_routes(app)
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"status": "error", "message": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"status": "error", "message": "Internal server error", "error": error}), 500


    

    return app