"""
NANOTRONICS SURVEY - Backend Flask
Production-ready backend with health checks, logging, and security
"""

import csv
import json
import os
import time
from collections import defaultdict
from datetime import datetime
from functools import wraps
from threading import Lock

from flask import Flask, request, jsonify, send_from_directory, g
from flask_cors import CORS

from config import Config, get_config

# =============================================================================
# Application Factory
# =============================================================================

def create_app(config_class=None):
    """Application factory pattern"""
    app = Flask(__name__, static_folder='.', static_url_path='')
    
    # Load configuration
    if config_class is None:
        config_class = get_config()
    
    app.config.from_object(config_class)
    
    # Initialize CORS
    CORS(app, origins=config_class.ALLOWED_ORIGINS)
    
    # Setup logging
    setup_logging(app)
    
    # Register middleware
    register_middleware(app)
    
    # Register routes
    register_routes(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Ensure responses directory exists
    responses_dir = config_class.RESPONSES_DIR
    if not os.path.exists(responses_dir):
        os.makedirs(responses_dir)
    
    # Validate configuration
    warnings = config_class.validate()
    for warning in warnings:
        app.logger.warning(f"Configuration warning: {warning}")
    
    app.logger.info(f"🚀 {config_class.APP_NAME} v{config_class.APP_VERSION} initialized")
    app.logger.info(f"📊 Environment: {config_class.FLASK_ENV}")
    
    return app


# =============================================================================
# Logging Setup
# =============================================================================

def setup_logging(app):
    """Configure structured logging"""
    import logging
    import sys
    
    config = get_config()
    
    # Set log level
    log_level = getattr(logging, config.LOG_LEVEL, logging.INFO)
    
    # Clear existing handlers
    app.logger.handlers.clear()
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # JSON format for production
    if config.LOG_FORMAT == 'json':
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage(),
                    'logger': record.name,
                }
                if hasattr(record, 'request_id'):
                    log_record['request_id'] = record.request_id
                if record.exc_info:
                    log_record['exception'] = self.formatException(record.exc_info)
                return json.dumps(log_record)
        
        handler.setFormatter(JSONFormatter())
    else:
        # Text format for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
    
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)
    
    # Reduce werkzeug logging in production
    if config.is_production():
        logging.getLogger('werkzeug').setLevel(logging.WARNING)


# =============================================================================
# Rate Limiting
# =============================================================================

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            # Clean old requests
            self.requests[key] = [
                t for t in self.requests[key] if t > window_start
            ]
            
            # Check limit
            if len(self.requests[key]) >= self.max_requests:
                return False
            
            # Add request
            self.requests[key].append(now)
            return True
    
    def get_remaining(self, key: str) -> int:
        """Get remaining requests for key"""
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds
            current = len([t for t in self.requests[key] if t > window_start])
            return max(0, self.max_requests - current)


# Global rate limiter instance
rate_limiter = None


def get_rate_limiter():
    """Get or create rate limiter"""
    global rate_limiter
    if rate_limiter is None:
        config = get_config()
        rate_limiter = RateLimiter(
            config.RATE_LIMIT_REQUESTS,
            config.RATE_LIMIT_WINDOW
        )
    return rate_limiter


def rate_limit(f):
    """Rate limiting decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        config = get_config()
        if not config.RATE_LIMIT_ENABLED:
            return f(*args, **kwargs)
        
        limiter = get_rate_limiter()
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        if not limiter.is_allowed(client_ip):
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.',
                'retry_after': config.RATE_LIMIT_WINDOW
            }), 429
        
        # Add rate limit headers
        response = f(*args, **kwargs)
        if isinstance(response, tuple):
            resp, status = response
        else:
            resp, status = response, 200
        
        return resp, status
    
    return decorated_function


# =============================================================================
# Middleware
# =============================================================================

def register_middleware(app):
    """Register middleware functions"""
    
    @app.before_request
    def before_request():
        """Execute before each request"""
        g.start_time = time.time()
        g.request_id = request.headers.get(
            'X-Request-ID', 
            f"{int(time.time() * 1000)}"
        )
    
    @app.after_request
    def after_request(response):
        """Execute after each request"""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add request ID header
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        # Log request (skip health checks to reduce noise)
        if not request.path.startswith('/health'):
            duration = time.time() - g.start_time if hasattr(g, 'start_time') else 0
            app.logger.info(
                f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s"
            )
        
        return response


# =============================================================================
# Routes
# =============================================================================

def register_routes(app):
    """Register all application routes"""
    config = get_config()
    
    # =========================================================================
    # Health Check Endpoints
    # =========================================================================
    
    @app.route('/health')
    def health_check():
        """Basic health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': config.APP_VERSION
        }), 200
    
    @app.route('/health/ready')
    def readiness_check():
        """Readiness check - verify app is ready to serve traffic"""
        checks = {
            'responses_dir': os.path.exists(config.RESPONSES_DIR),
        }
        
        all_ready = all(checks.values())
        status = 'ready' if all_ready else 'not_ready'
        
        return jsonify({
            'status': status,
            'checks': checks,
            'timestamp': datetime.utcnow().isoformat()
        }), 200 if all_ready else 503
    
    @app.route('/health/live')
    def liveness_check():
        """Liveness check - verify app is running"""
        return jsonify({
            'status': 'alive',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    # =========================================================================
    # Static Files
    # =========================================================================
    
    @app.route('/')
    def index():
        """Serve the main survey page"""
        return send_from_directory('.', 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files (CSS, JS)"""
        # Security: prevent directory traversal
        if '..' in path:
            return jsonify({'error': 'Invalid path'}), 400
        return send_from_directory('.', path)
    
    # =========================================================================
    # API Endpoints
    # =========================================================================
    
    @app.route('/api/submit', methods=['POST'])
    @rate_limit
    def submit_survey():
        """Handle survey submission"""
        try:
            # Validate content type
            if not request.is_json:
                return jsonify({
                    'error': 'Invalid content type',
                    'message': 'Content-Type must be application/json'
                }), 400
            
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'error': 'No data received',
                    'message': 'Request body is empty'
                }), 400
            
            # Add server metadata
            data['server_timestamp'] = datetime.utcnow().isoformat()
            data['client_ip'] = request.headers.get('X-Forwarded-For', request.remote_addr)
            data['user_agent'] = request.headers.get('User-Agent', 'unknown')
            
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f'response_{timestamp}.json'
            filepath = os.path.join(config.RESPONSES_DIR, filename)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Also append to master CSV
            append_to_csv(data, config.RESPONSES_DIR)
            
            app.logger.info(f"Survey response saved: {filename}")
            
            return jsonify({
                'success': True,
                'message': '¡Respuesta guardada correctamente!',
                'id': timestamp
            }), 200
            
        except Exception as e:
            app.logger.error(f'Error saving response: {e}', exc_info=True)
            return jsonify({
                'error': 'Internal server error',
                'message': 'Error processing your submission'
            }), 500
    
    @app.route('/api/responses', methods=['GET'])
    @rate_limit
    def get_responses():
        """Get all responses (for admin view)"""
        try:
            responses = []
            
            if not os.path.exists(config.RESPONSES_DIR):
                return jsonify({
                    'total': 0,
                    'responses': []
                }), 200
            
            for filename in os.listdir(config.RESPONSES_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(config.RESPONSES_DIR, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        responses.append(json.load(f))
            
            # Sort by timestamp (newest first)
            responses.sort(
                key=lambda x: x.get('server_timestamp', ''), 
                reverse=True
            )
            
            return jsonify({
                'total': len(responses),
                'responses': responses
            }), 200
            
        except Exception as e:
            app.logger.error(f'Error getting responses: {e}', exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats', methods=['GET'])
    @rate_limit
    def get_stats():
        """Get basic survey statistics"""
        try:
            responses = []
            
            if not os.path.exists(config.RESPONSES_DIR):
                return jsonify({
                    'total_responses': 0,
                    'message': 'No hay respuestas aún'
                }), 200
            
            for filename in os.listdir(config.RESPONSES_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(config.RESPONSES_DIR, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        responses.append(json.load(f))
            
            if not responses:
                return jsonify({
                    'total_responses': 0,
                    'message': 'No hay respuestas aún'
                }), 200
            
            # Calculate basic stats
            stats = {
                'total_responses': len(responses),
                'q1_distribution': count_values(responses, 'q1'),
                'q3_distribution': count_values(responses, 'q3'),
                'q6_average': calculate_average(responses, 'q6'),
                'q7_average': calculate_average(responses, 'q7_slider'),
                'q10_average': calculate_average(responses, 'q10_trust'),
            }
            
            return jsonify(stats), 200
            
        except Exception as e:
            app.logger.error(f'Error getting stats: {e}', exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/info', methods=['GET'])
    def get_info():
        """Get application information"""
        return jsonify({
            'app': config.APP_NAME,
            'version': config.APP_VERSION,
            'environment': config.FLASK_ENV,
        }), 200


# =============================================================================
# Helper Functions
# =============================================================================

def append_to_csv(data: dict, responses_dir: str):
    """Append response to master CSV file"""
    csv_file = os.path.join(responses_dir, 'all_responses.csv')
    file_exists = os.path.exists(csv_file)
    
    # Flatten nested data
    flat_data = {}
    for key, value in data.items():
        if isinstance(value, list):
            flat_data[key] = ', '.join(str(v) for v in value)
        else:
            flat_data[key] = str(value)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=flat_data.keys())
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(flat_data)


def count_values(responses: list, key: str) -> dict:
    """Count occurrences of each value for a key"""
    counts = {}
    for response in responses:
        value = response.get(key)
        if value:
            counts[value] = counts.get(value, 0) + 1
    return counts


def calculate_average(responses: list, key: str) -> float | None:
    """Calculate average for numeric values"""
    values = []
    for response in responses:
        value = response.get(key)
        if value:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    if values:
        return round(sum(values) / len(values), 2)
    return None


# =============================================================================
# Error Handlers
# =============================================================================

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Method Not Allowed',
            'message': f'Method {request.method} is not allowed for this endpoint'
        }), 405
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f'Internal server error: {error}', exc_info=True)
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500


# =============================================================================
# Application Instance
# =============================================================================

# Create app instance
app = create_app()


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == '__main__':
    config = get_config()
    print(f'🚀 {config.APP_NAME} v{config.APP_VERSION}')
    print(f'📊 Open http://localhost:{config.PORT} in your browser')
    print('-' * 40)
    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT
    )
