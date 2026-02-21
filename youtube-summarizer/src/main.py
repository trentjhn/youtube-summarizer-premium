import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
# Get the directory where this file is located (src/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the youtube-summarizer directory
project_root = os.path.dirname(current_dir)
env_file = os.path.join(project_root, '.env')
print(f"Loading .env from: {env_file}")
print(f"File exists: {os.path.exists(env_file)}")
# Load with override=True to ensure .env values take precedence
load_dotenv(env_file, override=True)

# Check for Google AI API key (primary) or fallback to GEMINI_API_KEY
google_api_key = os.environ.get('GOOGLE_AI_API_KEY') or os.environ.get('GEMINI_API_KEY')
print(f"GOOGLE_AI_API_KEY loaded: {bool(google_api_key)}")
if google_api_key:
    print(f"API Key first 20 chars: {google_api_key[:20]}")
    print(f"API Key length: {len(google_api_key)}")
else:
    print("WARNING: No Google AI API key found. Set GOOGLE_AI_API_KEY environment variable.")

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.video import db, Video
from src.routes.video import video_bp
from src.routes.websocket_events import init_websocket
from src.middleware import create_limiter, init_rate_limiting

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Enable CORS for frontend communication
CORS(app)

# Initialize rate limiting
limiter = create_limiter()
init_rate_limiting(app, limiter)

# Initialize WebSocket for real-time progress updates
socketio = init_websocket(app)

app.register_blueprint(video_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/api/admin/clear-cache', methods=['POST'])
def clear_cache():
    """
    Admin endpoint to clear all cached video summaries from the database.

    This endpoint deletes all entries from the videos table, forcing fresh
    generation of summaries for all videos. Useful for:
    - Testing prompt changes without version increment
    - Major cleanup operations
    - Development and debugging

    Returns:
        JSON response with success status and count of deleted entries
    """
    try:
        # Count entries before deletion
        count_before = Video.query.count()

        # Delete all video entries from database
        Video.query.delete()
        db.session.commit()

        logger.info(f"Cache cleared: {count_before} video entries deleted")

        return jsonify({
            'success': True,
            'message': f'Cache cleared successfully. {count_before} entries deleted.',
            'deleted_count': count_before
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error clearing cache: {e}")

        return jsonify({
            'success': False,
            'message': f'Failed to clear cache: {str(e)}',
            'deleted_count': 0
        }), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Don't serve static files for API routes
    if path.startswith('api/'):
        return "Not found", 404

    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
