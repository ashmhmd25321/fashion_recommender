import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///fashion.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Define the base directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Define upload folder paths
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    IMAGES_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
    
    # Ensure these directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(IMAGES_FOLDER, exist_ok=True)
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload 