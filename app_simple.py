from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, ClothingItem, Vote, SustainabilityFactor, Role
from recommender import FashionRecommender
from config import Config
from functools import wraps
import os
import uuid

app = Flask(__name__)
app.config.from_object(Config)

# Add custom filter for normalizing file paths
@app.template_filter('normalize_path')
def normalize_path(path):
    """Convert Windows backslash paths to forward slash paths for URLs"""
    if path:
        return path.replace('\\', '/')
    return path

# Ensure static directories exist
static_folder = os.path.join(app.root_path, 'static')
os.makedirs(static_folder, exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['IMAGES_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize recommender
recommender = FashionRecommender()

# Create database tables and add initial data
def create_tables():
    with app.app_context():
        db.create_all()
        
        # Add some initial sustainability factors if none exist
        if SustainabilityFactor.query.count() == 0:
            factors = [
                SustainabilityFactor(name="Material", description="The type of material used in the clothing item", weight=1.5),
                SustainabilityFactor(name="Manufacturing Process", description="How the item was manufactured", weight=1.2),
                SustainabilityFactor(name="Water Usage", description="Amount of water used in production", weight=1.0),
                SustainabilityFactor(name="Carbon Footprint", description="Carbon emissions during production", weight=1.3),
                SustainabilityFactor(name="Durability", description="How long the item is expected to last", weight=0.8)
            ]
            db.session.add_all(factors)
            db.session.commit()
            
        # Create default admin user if no admin exists
        admin_exists = User.query.filter_by(role=Role.ADMIN).first()
        if not admin_exists:
            admin = User(
                username="admin",
                email="admin@example.com",
                role=Role.ADMIN
            )
            admin.set_password("admin123")  # Set a default password
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created with username 'admin' and password 'admin123'")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    # Get some featured clothing items
    featured_items = ClothingItem.query.order_by(ClothingItem.created_at.desc()).limit(6).all()
    
    # Normalize paths for all items
    for item in featured_items:
        item.image_path = normalize_path(item.image_path)
    
    return render_template('index.html', featured_items=featured_items)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
            
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('login.html')
            
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
            
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard')
            
        return redirect(next_page)
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_items = ClothingItem.query.filter_by(user_id=current_user.id).all()
    
    # Normalize paths for all items
    for item in user_items:
        item.image_path = normalize_path(item.image_path)
    
    user_votes = Vote.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', items=user_items, votes=user_votes)

@app.route('/recommend', methods=['GET', 'POST'])
@login_required
def recommend():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = str(uuid.uuid4()) + secure_filename(file.filename)
            
            # Ensure upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # Complete file path
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file
            file.save(file_path)
            
            # Verify file was saved
            if not os.path.exists(file_path):
                flash('Error saving file. Please try again.', 'danger')
                return redirect(request.url)
                
            # Get recommendations
            recommendations = recommender.recommend(file_path, num_recommendations=5)
            
            # Check sustainability
            sustainability = recommender.check_sustainability(file_path)
            
            # Create a new clothing item
            item_name = request.form.get('item_name', 'Unnamed Item')
            item_description = request.form.get('item_description', '')
            
            # Store the relative path from static folder - ensure it's correctly formatted
            # The path must be relative to the static folder without including 'static/'
            # This path should be 'uploads/filename.jpg' not '/uploads/filename.jpg' or 'static/uploads/filename.jpg'
            # Always use forward slashes for web paths, even on Windows
            relative_path = 'uploads/' + filename  # Use forward slash for web paths
            app.logger.info(f"Saving image with path: {relative_path}")
            
            new_item = ClothingItem(
                name=item_name,
                description=item_description,
                image_path=relative_path,  # Store relative path
                sustainability_score=sustainability['score'],
                sustainability_notes=f"Material: {sustainability['material']}. {sustainability['notes']} {sustainability['recommendation']}",
                user_id=current_user.id
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            # Convert recommendation paths to web-friendly paths
            web_recommendations = []
            for rec_path in recommendations:
                # Extract just the filename from the path
                rec_filename = os.path.basename(rec_path)
                # Construct a path relative to the static folder
                web_path = os.path.join('images', rec_filename)
                web_recommendations.append(web_path)
            
            return render_template(
                'recommend_results.html',
                item=new_item,
                recommendations=web_recommendations,
                sustainability=sustainability
            )
            
    return render_template('recommend.html')

@app.route('/items')
def items():
    page = request.args.get('page', 1, type=int)
    items_pagination = ClothingItem.query.order_by(ClothingItem.created_at.desc()).paginate(page=page, per_page=12)
    
    # Normalize paths for all items
    for item in items_pagination.items:
        item.image_path = normalize_path(item.image_path)
    
    return render_template('items.html', items=items_pagination)

@app.route('/item/<int:item_id>')
def item_details(item_id):
    item = ClothingItem.query.get_or_404(item_id)
    
    # Normalize image path
    item.image_path = normalize_path(item.image_path)
    
    user_vote = None
    if current_user.is_authenticated:
        user_vote = Vote.query.filter_by(user_id=current_user.id, item_id=item.id).first()
    return render_template('item_details.html', item=item, user_vote=user_vote)

@app.route('/vote/<int:item_id>', methods=['POST'])
@login_required
def vote(item_id):
    item = ClothingItem.query.get_or_404(item_id)
    
    try:
        vote_value = int(request.form.get('vote'))
        if vote_value < 1 or vote_value > 5:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Vote must be between 1 and 5'})
            flash('Vote must be between 1 and 5', 'danger')
            return redirect(url_for('item_details', item_id=item.id))
    except:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Invalid vote value'})
        flash('Invalid vote value', 'danger')
        return redirect(url_for('item_details', item_id=item.id))
        
    comment = request.form.get('comment', '')
    
    # Check if user already voted for this item
    existing_vote = Vote.query.filter_by(user_id=current_user.id, item_id=item.id).first()
    
    if existing_vote:
        # Update existing vote
        existing_vote.value = vote_value
        existing_vote.comment = comment
        message = 'Your vote has been updated'
    else:
        # Create new vote
        new_vote = Vote(
            value=vote_value,
            comment=comment,
            user_id=current_user.id,
            item_id=item.id
        )
        db.session.add(new_vote)
        message = 'Your vote has been recorded'
        
    db.session.commit()
    
    # If AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Calculate the new average score
        new_score = item.get_vote_score()
        votes_count = item.votes.count()
        
        return jsonify({
            'success': True,
            'message': message,
            'new_score': round(new_score, 1),
            'votes_count': votes_count
        })
    
    # For regular form submission
    flash(message, 'success')
    return redirect(url_for('item_details', item_id=item.id))

@app.route('/sustainability')
def sustainability():
    factors = SustainabilityFactor.query.all()
    # Get some sample items to display
    sample_items = ClothingItem.query.order_by(ClothingItem.sustainability_score.desc()).limit(6).all()
    
    # Normalize paths for all items
    for item in sample_items:
        item.image_path = normalize_path(item.image_path)
        
    return render_template('sustainability.html', factors=factors, sample_items=sample_items)

@app.route('/sustainability/check', methods=['GET', 'POST'])
def sustainability_check():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            # Generate unique filename (temporary)
            filename = str(uuid.uuid4()) + secure_filename(file.filename)
            
            # Ensure upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # Complete file path
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file temporarily
            file.save(file_path)
            
            # Verify file was saved
            if not os.path.exists(file_path):
                flash('Error saving file. Please try again.', 'danger')
                return redirect(request.url)
            
            # Check sustainability without saving to database
            sustainability = recommender.check_sustainability(file_path)
            
            # Relative path for displaying the image
            relative_path = os.path.join('uploads', filename).replace('\\', '/')
            
            return render_template(
                'sustainability_result.html', 
                sustainability=sustainability, 
                image_path=relative_path,
                factors=SustainabilityFactor.query.all()
            )
    
    return render_template('sustainability_check.html')

@app.route('/debug/images')
@login_required
def debug_images():
    """Debug route to check image paths and if files exist"""
    result = {
        'items': [],
        'static_folder': os.path.abspath(os.path.join(app.root_path, 'static')),
        'upload_folder': os.path.abspath(app.config['UPLOAD_FOLDER']),
        'upload_folder_exists': os.path.exists(app.config['UPLOAD_FOLDER']),
        'upload_files': os.listdir(app.config['UPLOAD_FOLDER']) if os.path.exists(app.config['UPLOAD_FOLDER']) else []
    }
    
    # Check user's items
    items = ClothingItem.query.filter_by(user_id=current_user.id).all()
    for item in items:
        # Build the full file path
        file_path = os.path.join(app.root_path, 'static', item.image_path)
        
        item_data = {
            'id': item.id,
            'name': item.name,
            'image_path': item.image_path,
            'full_path': file_path,
            'file_exists': os.path.exists(file_path),
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        }
        result['items'].append(item_data)
    
    return jsonify(result)

@app.route('/api/items', methods=['GET'])
def api_items():
    items = ClothingItem.query.order_by(ClothingItem.created_at.desc()).limit(50).all()
    result = []
    for item in items:
        result.append({
            'id': item.id,
            'name': item.name,
            'image_path': item.image_path,
            'sustainability_score': item.sustainability_score,
            'vote_score': item.get_vote_score(),
            'votes_count': item.votes.count()
        })
    return jsonify(result)

@app.route('/api/vote/<int:item_id>', methods=['POST'])
@login_required
def api_vote(item_id):
    item = ClothingItem.query.get_or_404(item_id)
    
    data = request.get_json()
    if not data or 'value' not in data:
        return jsonify({'error': 'Vote value is required'}), 400
        
    try:
        vote_value = int(data['value'])
        if vote_value < 1 or vote_value > 5:
            return jsonify({'error': 'Vote must be between 1 and 5'}), 400
    except:
        return jsonify({'error': 'Invalid vote value'}), 400
        
    comment = data.get('comment', '')
    
    # Check if user already voted for this item
    existing_vote = Vote.query.filter_by(user_id=current_user.id, item_id=item.id).first()
    
    if existing_vote:
        # Update existing vote
        existing_vote.value = vote_value
        existing_vote.comment = comment
        message = 'Vote updated'
    else:
        # Create new vote
        new_vote = Vote(
            value=vote_value,
            comment=comment,
            user_id=current_user.id,
            item_id=item.id
        )
        db.session.add(new_vote)
        message = 'Vote recorded'
        
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': message,
        'new_score': item.get_vote_score(),
        'votes_count': item.votes.count()
    })

@app.route('/api/sustainability', methods=['POST'])
def api_sustainability():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = str(uuid.uuid4()) + secure_filename(file.filename)
        
        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Complete file path with forward slashes for web compatibility
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
        
        # Save the file
        file.save(file_path)
        
        # Verify file was saved
        if not os.path.exists(file_path):
            flash('Error saving file. Please try again.', 'danger')
            return redirect(request.url)
            
        # Check sustainability
        sustainability = recommender.check_sustainability(file_path)
        
        return jsonify(sustainability)
    
    return jsonify({'error': 'Invalid file type'}), 400

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ADMIN ROUTES

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard with product and user management options"""
    items_count = ClothingItem.query.count()
    users_count = User.query.count()
    votes_count = Vote.query.count()
    
    # Get recent items
    recent_items = ClothingItem.query.order_by(ClothingItem.created_at.desc()).limit(5).all()
    
    # Normalize paths
    for item in recent_items:
        item.image_path = normalize_path(item.image_path)
    
    return render_template(
        'admin/dashboard.html',
        items_count=items_count,
        users_count=users_count,
        votes_count=votes_count,
        recent_items=recent_items
    )

@app.route('/admin/products')
@login_required
@admin_required
def admin_products():
    """Product management page for admins"""
    page = request.args.get('page', 1, type=int)
    products = ClothingItem.query.order_by(ClothingItem.created_at.desc()).paginate(page=page, per_page=10)
    
    # Normalize paths
    for item in products.items:
        item.image_path = normalize_path(item.image_path)
    
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_product_create():
    """Create new product as admin"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = str(uuid.uuid4()) + secure_filename(file.filename)
            
            # Ensure upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # Complete file path
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file
            file.save(file_path)
            
            # Verify file was saved
            if not os.path.exists(file_path):
                flash('Error saving file. Please try again.', 'danger')
                return redirect(request.url)
            
            # Get form data
            item_name = request.form.get('item_name', 'Unnamed Item')
            item_description = request.form.get('item_description', '')
            
            # Check sustainability
            sustainability = recommender.check_sustainability(file_path)
            
            # Store the relative path with forward slashes for web compatibility
            relative_path = 'uploads/' + filename
            
            # Create new product
            new_item = ClothingItem(
                name=item_name,
                description=item_description,
                image_path=relative_path,
                sustainability_score=sustainability['score'],
                sustainability_notes=f"Material: {sustainability['material']}. {sustainability['notes']} {sustainability['recommendation']}",
                user_id=current_user.id
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            flash('Product added successfully!', 'success')
            return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html')

@app.route('/admin/products/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_product_edit(item_id):
    """Edit existing product as admin"""
    item = ClothingItem.query.get_or_404(item_id)
    
    if request.method == 'POST':
        # Update basic information
        item.name = request.form.get('item_name', item.name)
        item.description = request.form.get('item_description', item.description)
        
        # Check if new image was uploaded
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            
            if allowed_file(file.filename):
                # Generate unique filename
                filename = str(uuid.uuid4()) + secure_filename(file.filename)
                
                # Ensure upload directory exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                # Complete file path
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Save the file
                file.save(file_path)
                
                # Verify file was saved
                if not os.path.exists(file_path):
                    flash('Error saving file. Please try again.', 'danger')
                    return redirect(request.url)
                
                # Update path in database (use forward slashes)
                item.image_path = 'uploads/' + filename
                
                # Update sustainability based on new image
                sustainability = recommender.check_sustainability(file_path)
                item.sustainability_score = sustainability['score']
                item.sustainability_notes = f"Material: {sustainability['material']}. {sustainability['notes']} {sustainability['recommendation']}"
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    # Normalize path for template
    item.image_path = normalize_path(item.image_path)
    
    return render_template('admin/product_form.html', item=item)

@app.route('/admin/products/<int:item_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_product_delete(item_id):
    """Delete product as admin"""
    item = ClothingItem.query.get_or_404(item_id)
    
    # Delete the image file
    full_path = os.path.join(app.root_path, 'static', item.image_path)
    try:
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception as e:
        app.logger.error(f"Error deleting file: {e}")
    
    # Delete all votes for this item
    Vote.query.filter_by(item_id=item.id).delete()
    
    # Delete the item
    db.session.delete(item)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """User management page for admins"""
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<int:user_id>/toggle-role', methods=['POST'])
@login_required
@admin_required
def admin_toggle_user_role(user_id):
    """Toggle a user's role between admin and customer"""
    user = User.query.get_or_404(user_id)
    
    # Don't allow changing your own role
    if user.id == current_user.id:
        flash('You cannot change your own role.', 'danger')
        return redirect(url_for('admin_users'))
    
    # Toggle role
    if user.role == Role.ADMIN:
        user.role = Role.CUSTOMER
        flash(f'User {user.username} is now a customer.', 'success')
    else:
        user.role = Role.ADMIN
        flash(f'User {user.username} is now an admin.', 'success')
    
    db.session.commit()
    return redirect(url_for('admin_users'))

@app.route('/admin/ratings')
@login_required
@admin_required
def admin_ratings():
    """View all ratings for admin management"""
    page = request.args.get('page', 1, type=int)
    votes = Vote.query.join(ClothingItem).order_by(Vote.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/ratings.html', votes=votes)

@app.route('/admin/ratings/<int:vote_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_rating_delete(vote_id):
    """Delete a vote/rating as admin"""
    vote = Vote.query.get_or_404(vote_id)
    db.session.delete(vote)
    db.session.commit()
    
    flash('Rating deleted successfully!', 'success')
    return redirect(url_for('admin_ratings'))

if __name__ == '__main__':
    # Create tables before running the app
    create_tables()
    app.run(debug=True, port=5001)  # Use a different port than your Streamlit app 