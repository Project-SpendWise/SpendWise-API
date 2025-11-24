from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from config import config
import os
import logging
import time
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
cors = CORS()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Configure logging
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        # Only configure logging once (avoid duplicate logs in debug mode)
        logging.basicConfig(
            level=logging.INFO if config_name == 'production' else logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Get logger for this app
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if config_name == 'development' else logging.INFO)
    
    # Validate production config
    if config_name == 'production':
        if not app.config.get('SECRET_KEY') or not app.config.get('JWT_SECRET_KEY'):
            raise ValueError("SECRET_KEY and JWT_SECRET_KEY must be set in production")
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Range"],
            "expose_headers": ["Content-Length", "Content-Range", "Accept-Ranges", "Content-Disposition"]
        }
    })
    
    # Import all models to ensure they're registered with SQLAlchemy
    from models import User, File, Statement, Transaction, Budget
    
    # Register blueprints (models will be imported by routes)
    from routes.auth import auth_bp
    from routes.files import files_bp
    from routes.statements import statements_bp
    from routes.transactions import transactions_bp
    from routes.budgets import budgets_bp
    from routes.analytics import analytics_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(files_bp, url_prefix='/api/files')
    app.register_blueprint(statements_bp, url_prefix='/api/statements')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(budgets_bp, url_prefix='/api/budgets')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Ensure models are registered with db and create tables
    with app.app_context():
        db.create_all()
    
    # Create upload directory if it doesn't exist
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder and not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        logger.info(f"Created upload directory: {upload_folder}")
    
    # Request logging middleware
    @app.before_request
    def log_request_info():
        """Log incoming request information"""
        g.start_time = time.time()
        logger.info(
            f"REQUEST: {request.method} {request.path} | "
            f"IP: {request.remote_addr} | "
            f"User-Agent: {request.headers.get('User-Agent', 'Unknown')[:50]}"
        )
        
        # Log request body for non-GET requests (excluding file uploads)
        if request.method != 'GET' and request.is_json:
            try:
                data = request.get_json()
                # Don't log sensitive data like passwords
                if 'password' in str(data).lower():
                    logger.debug("Request body contains sensitive data (not logged)")
                else:
                    logger.debug(f"Request body: {data}")
            except Exception:
                pass
    
    @app.after_request
    def log_response_info(response):
        """Log response information"""
        duration = time.time() - g.start_time if hasattr(g, 'start_time') else 0
        logger.info(
            f"RESPONSE: {request.method} {request.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.3f}s"
        )
        return response
    
    # Error handlers
    from utils.responses import error_response
    from werkzeug.exceptions import BadRequest, Unauthorized, NotFound, InternalServerError
    import traceback
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"Bad Request: {request.method} {request.path} - {str(error)}")
        return error_response('Bad Request', 'BAD_REQUEST', 400), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning(f"Unauthorized: {request.method} {request.path} - {str(error)}")
        return error_response('Unauthorized', 'UNAUTHORIZED', 401), 401
    
    @app.errorhandler(404)
    def not_found(error):
        logger.info(f"Not Found: {request.method} {request.path}")
        return error_response('Resource not found', 'NOT_FOUND', 404), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(
            f"Internal Server Error: {request.method} {request.path}\n"
            f"Error: {str(error)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        return error_response('Internal server error', 'INTERNAL_ERROR', 500), 500
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.warning(f"Expired token attempt: {request.method} {request.path}")
        return error_response('Token has expired', 'TOKEN_EXPIRED', 401), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        logger.warning(f"Invalid token attempt: {request.method} {request.path} - {str(error)}")
        return error_response('Invalid token', 'INVALID_TOKEN', 401), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        logger.warning(f"Missing token: {request.method} {request.path}")
        return error_response('Authorization token is missing', 'MISSING_TOKEN', 401), 401
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        logger.debug("Health check requested")
        return {'status': 'healthy', 'service': 'SpendWise API'}, 200
    
    logger.info(f"Application initialized in {config_name} mode")
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    # Configure timeout for file downloads (60 seconds minimum)
    # Note: For production, use a proper WSGI server like Gunicorn with timeout settings
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)

