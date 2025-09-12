import pickle
# Removing tensorflow imports which are causing errors
# import tensorflow
import numpy as np
# from numpy.linalg import norm
# from tensorflow.keras.preprocessing import image
# from tensorflow.keras.layers import GlobalMaxPooling2D
# from tensorflow.keras.applications.resnet50 import ResNet50,preprocess_input
from sklearn.neighbors import NearestNeighbors
# import cv2
import streamlit as st
import os
from PIL import Image
import glob
import time
import random
import tempfile
import io

# Configure Streamlit page
st.set_page_config(
    page_title="Fashion Recommender",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better image display
st.markdown("""
<style>
    /* Page title styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 1rem;
        text-align: center;
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 10px 0;
    }
    
    /* Enhance image display */
    .stImage > img {
        border-radius: 10px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        background-color: white;
        padding: 8px;
    }
    
    .stImage > img:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        cursor: pointer;
    }
    
    /* Image caption styling */
    .stImage > div > p {
        margin-top: 8px;
        font-weight: 500;
        color: #555;
    }
    
    /* Container styling */
    .image-container {
        border-radius: 12px;
        padding: 10px;
        background: linear-gradient(145deg, #f0f0f0, #ffffff);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* Uploaded image specific styling */
    .uploaded-image {
        border: 2px solid #4CAF50;
    }
    
    /* Recommendation image specific styling */
    .recommendation-image {
        border: 2px solid #2196F3;
    }
    
    /* Section headers */
    h3 {
        font-weight: 600;
        color: #333;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

# Function to safely handle file operations
def safe_remove_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except PermissionError:
        st.warning(f"Could not remove {file_path} as it is being used by another process.")
        return False
    except Exception as e:
        st.warning(f"Error removing {file_path}: {e}")
        return False
    return True

# Back to Dashboard button at the top
st.markdown("""
<div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
    <a href="http://localhost:5001/dashboard" target="_self" style="
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: #4CAF50;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        font-weight: bold;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    ">← Back to Dashboard</a>
</div>
""", unsafe_allow_html=True)

# Create directories if they don't exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('images', exist_ok=True)

# Set consistent image dimensions
IMAGE_WIDTH = 50
IMAGE_HEIGHT = 50
FEATURE_DIMENSION = IMAGE_WIDTH * IMAGE_HEIGHT

# Use session state to track app state
if 'ready' not in st.session_state:
    st.session_state.ready = False
    st.session_state.model_loaded = False
    # Only try to remove files if explicitly requested
    if 'force_regenerate' in st.session_state and st.session_state.force_regenerate:
        st.info("Attempting to regenerate features as requested...")
        try:
            safe_remove_file('embeddings_simple.pkl')
            safe_remove_file('filenames_simple.pkl')
        except Exception as e:
            st.warning(f"Error during file cleanup: {e}")
        finally:
            # Reset the flag
            st.session_state.force_regenerate = False

# Cache the feature data loading
@st.cache_data(ttl=3600, show_spinner=False)
def load_feature_data():
    if os.path.exists('embeddings_simple.pkl') and os.path.exists('filenames_simple.pkl'):
        feature_list = np.array(pickle.load(open('embeddings_simple.pkl', 'rb')))
        filenames = pickle.load(open('filenames_simple.pkl', 'rb'))
        return feature_list, filenames
    return None, None

# Cache the nearest neighbors model initialization
@st.cache_resource(show_spinner=False)
def get_neighbors_model(feature_list, n_neighbors, algorithm='brute'):
    neighbors = NearestNeighbors(n_neighbors=n_neighbors, algorithm=algorithm, metric='euclidean')
    neighbors.fit(feature_list)
    return neighbors

# Cache feature extraction - ensure consistent dimensions
@st.cache_data(show_spinner=False)
def extract_features(img_path):
    try:
        # Use consistent image size for feature extraction
        img = Image.open(img_path).convert('L').resize((IMAGE_WIDTH, IMAGE_HEIGHT))
        img_array = np.array(img)
        
        # Extract features (flatten the image)
        features = img_array.flatten()
        
        # Normalize features
        features = features / 255.0
        
        return features
    except Exception as e:
        st.error(f"Error processing {img_path}: {e}")
        return None

# Function to extract features from an uploaded file
def extract_features_from_uploaded(uploaded_file):
    try:
        # Create a bytes buffer from the uploaded file
        bytes_data = io.BytesIO(uploaded_file.getvalue())
        
        # Use PIL to open the image from the bytes buffer
        img = Image.open(bytes_data).convert('L').resize((IMAGE_WIDTH, IMAGE_HEIGHT))
        img_array = np.array(img)
        
        # Extract features (flatten the image)
        features = img_array.flatten()
        
        # Normalize features
        features = features / 255.0
        
        return features
    except Exception as e:
        st.error(f"Error processing uploaded file: {e}")
        return None

# Function to save uploaded file
def save_uploaded_file(uploaded_file):
    try:
        with open(os.path.join('uploads', uploaded_file.name), 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return 1
    except Exception as e:
        st.error(f"Error saving uploaded file: {e}")
        return 0

# Function to generate features for all images
@st.cache_data(ttl=3600, show_spinner=False)
def generate_features(image_files):
    feature_list = []
    filenames = []
    
    for file in image_files:
        try:
            features = extract_features(file)
            if features is not None:
                feature_list.append(features)
                filenames.append(file)
        except Exception as e:
            # Log the error but continue processing other files
            st.warning(f"Skipping {file}: {e}")
    
    return np.array(feature_list), filenames

# Function to recommend similar images
def recommend(features, neighbors_model, num_recommendations=5):
    distances, indices = neighbors_model.kneighbors([features])
    return indices[0][1:]  # Skip the first one as it's the image itself

# Sidebar configuration
st.sidebar.title("Configuration")

# Add return to dashboard button in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center;">
    <a href="http://localhost:5001/dashboard" target="_self" style="
        display: inline-block;
        width: 100%;
        padding: 0.5rem;
        background-color: #4CAF50;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    ">Return to Dashboard</a>
</div>
""", unsafe_allow_html=True)

# Main app title with loading spinner
if not st.session_state.ready:
    with st.spinner("Loading Fashion Recommender System..."):
        # Load or generate feature files
        feature_list, filenames = load_feature_data()
        
        if feature_list is None or len(feature_list) == 0:
            # Check for images
            image_files = glob.glob('images/*.jpg') + glob.glob('images/*.jpeg') + glob.glob('images/*.png')
            
            if not image_files:
                st.warning("No images found in the 'images' directory. Please add some images to the 'images' directory.")
            else:
                # Randomly select 50% of the images for training
                random.seed(42)  # For reproducibility
                selected_files = random.sample(image_files, k=len(image_files)//2)
                
                with st.spinner(f"Generating features for {len(selected_files)} images (50% of total)..."):
                    feature_list, filenames = generate_features(selected_files)
                    
                    # Save features and filenames
                    if len(feature_list) > 0:
                        with open('embeddings_simple.pkl', 'wb') as f:
                            pickle.dump(feature_list, f)
                        
                        with open('filenames_simple.pkl', 'wb') as f:
                            pickle.dump(filenames, f)
                        
                        st.success(f"Feature embeddings generated successfully for {len(filenames)} images!")
                    else:
                        st.error("No valid images found to process.")
        
        # Set session state
        st.session_state.ready = True
        st.session_state.feature_list = feature_list
        st.session_state.filenames = filenames

# Display main UI once loaded
if st.session_state.ready:
    # Custom title with styling
    st.markdown('<h1 class="main-title">Fashion Recommender System</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; margin-bottom: 2rem;">Upload an image to find similar fashion items</p>', unsafe_allow_html=True)
    
    # Display info about dataset
    if hasattr(st.session_state, 'filenames') and st.session_state.filenames and len(st.session_state.filenames) > 0:
        st.sidebar.info(f"Number of images in database: {len(st.session_state.filenames)}")
        
        # Settings in sidebar
        num_recommendations = st.sidebar.slider("Number of recommendations", min_value=1, max_value=10, value=5)
        image_size = st.sidebar.slider("Image size", min_value=200, max_value=500, value=300)
        
        # Add image quality selector
        image_quality = st.sidebar.select_slider(
            "Image Quality",
            options=["Low", "Medium", "High"],
            value="Medium"
        )
        
        # Map quality setting to actual resize dimensions for feature extraction
        # Higher quality means images are displayed with better resolution
        quality_map = {
            "Low": (IMAGE_WIDTH, IMAGE_HEIGHT),
            "Medium": (IMAGE_WIDTH*2, IMAGE_HEIGHT*2),
            "High": (IMAGE_WIDTH*4, IMAGE_HEIGHT*4)
        }
        
        # Regenerate features button
        if st.sidebar.button("Regenerate features"):
            st.session_state.ready = False
            success = True
            if not safe_remove_file('embeddings_simple.pkl'):
                success = False
            if not safe_remove_file('filenames_simple.pkl'):
                success = False
            
            if success:
                st.experimental_rerun()
            else:
                st.warning("Could not regenerate features due to file access issues. Please close any other applications that might be using these files and try again.")
                # Set a flag to try again on next startup
                st.session_state.force_regenerate = True
        
        # File uploader
        uploaded_file = st.file_uploader("Choose an image")
        
        if uploaded_file is not None:
            tmp_file_path = None
            try:
                # Try to directly extract features from the uploaded file
                features = extract_features_from_uploaded(uploaded_file)
                
                # If direct extraction fails, try with temporary file
                if features is None:
                    # Create a temporary file to save the uploaded file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        # Write the uploaded file's content to the temporary file
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    # Open the image from the temporary file path
                    display_image = Image.open(tmp_file_path)
                    
                    # Extract features from the temp file
                    features = extract_features(tmp_file_path)
                else:
                    # Reopen the file for display
                    bytes_data = io.BytesIO(uploaded_file.getvalue())
                    display_image = Image.open(bytes_data)
                
                # Save the uploaded file for future use
                save_uploaded_file(uploaded_file)
                
                # Start a placeholder for the recommendations
                recommendation_placeholder = st.empty()
                
                with recommendation_placeholder.container():
                    # Display the uploaded image
                    st.markdown("<h3>Your Uploaded Image</h3>", unsafe_allow_html=True)
                    st.markdown('<div class="image-container">', unsafe_allow_html=True)
                    
                    # Enhance the uploaded image for better display
                    try:
                        enhanced_image = enhance_image_for_display(display_image, image_quality)
                    except Exception as e:
                        enhanced_image = display_image  # Fall back to original if enhancement fails
                    
                    st.image(
                        enhanced_image, 
                        caption="Uploaded Image", 
                        width=image_size + 100,
                        use_container_width=False
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Show a spinner while processing
                    with st.spinner("Processing your image..."):
                        if features is not None:
                            start_time = time.time()
                            
                            # Initialize the model with the correct number of neighbors
                            n_neighbors = min(num_recommendations + 1, len(st.session_state.feature_list))
                            n_neighbors = max(2, n_neighbors)  # At least 2 to get 1 recommendation after skipping self
                            
                            neighbors_model = get_neighbors_model(st.session_state.feature_list, n_neighbors)
                            
                            # Get recommendations
                            indices = recommend(features, neighbors_model, num_recommendations)
                            
                            # Show processing time
                            processing_time = time.time() - start_time
                            st.info(f"Processing time: {processing_time:.2f} seconds")
                            
                            if len(indices) > 0:
                                # Show recommendations
                                st.markdown("<h3>Recommended Items</h3>", unsafe_allow_html=True)
                                
                                # Create columns for displaying images
                                num_cols = min(3, len(indices))  # Limit to 3 columns for better visibility
                                
                                if num_cols > 0:  # Ensure we don't divide by zero
                                    rows = (len(indices) + num_cols - 1) // num_cols  # Calculate number of rows needed
                                    
                                    for row in range(rows):
                                        cols = st.columns(num_cols)
                                        for col_idx, col in enumerate(cols):
                                            idx = row * num_cols + col_idx
                                            if idx < len(indices):
                                                with col:
                                                    try:
                                                        img_path = st.session_state.filenames[indices[idx]]
                                                        img = Image.open(img_path)
                                                        
                                                        # Resize for better quality based on quality setting
                                                        resize_width, resize_height = quality_map[image_quality]
                                                        if max(img.size) > max(resize_width, resize_height):
                                                            img = img.copy()  # Create a copy to avoid modifying the original
                                                        
                                                        # Enhance image quality
                                                        try:
                                                            img = enhance_image_for_display(img, image_quality)
                                                        except Exception as e:
                                                            # If enhancement fails, just use the original
                                                            pass
                                                        
                                                        st.markdown('<div class="image-container">', unsafe_allow_html=True)
                                                        st.image(
                                                            img, 
                                                            width=image_size, 
                                                            caption=os.path.basename(img_path),
                                                            use_container_width=False
                                                        )
                                                        st.markdown('</div>', unsafe_allow_html=True)
                                                        
                                                        # Add some item metadata if available
                                                        filename = os.path.basename(img_path)
                                                        st.markdown(f"<p style='text-align: center;'><b>{filename}</b></p>", unsafe_allow_html=True)
                                                    except Exception as e:
                                                        st.error(f"Error displaying image: {e}")
                            else:
                                st.warning("No recommendations found. Try uploading a different image.")
                        else:
                            st.error("Failed to extract features from the uploaded image.")
                
            except Exception as e:
                st.error(f"Error processing image: {e}")
                st.info("Please try uploading a different image file. Make sure it's a valid image format (JPG, PNG, etc.)")
            
            finally:
                # Clean up the temporary file if it exists
                if tmp_file_path and os.path.exists(tmp_file_path):
                    try:
                        os.unlink(tmp_file_path)
                    except Exception as e:
                        pass  # Silently ignore cleanup errors
            
            # Add a prominent return to dashboard button at the bottom
            st.markdown("""
            <div style="margin-top: 2rem; text-align: center;">
                <a href="http://localhost:5001/dashboard" target="_self" style="
                    display: inline-block;
                    padding: 0.75rem 1.5rem;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 1.1rem;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                ">Return to Dashboard</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Please add some images to the 'images' directory and run the app again.")

# Function to enhance image for display (improve quality)
def enhance_image_for_display(img, quality="Medium"):
    # Make a copy to avoid modifying the original
    img = img.copy()
    
    # Apply some basic enhancements
    from PIL import ImageEnhance, ImageFilter, Image
    import numpy as np
    
    # First, resize the image to improve resolution
    # Get original size
    original_width, original_height = img.size
    
    # Define minimum display dimensions based on quality
    min_display_dims = {
        "Low": max(original_width, 300),
        "Medium": max(original_width, 450),
        "High": max(original_width, 600)
    }
    
    # Calculate new dimensions while preserving aspect ratio
    min_dim = min_display_dims.get(quality, min_display_dims["Medium"])
    if max(original_width, original_height) < min_dim:
        scale_factor = min_dim / max(original_width, original_height)
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        # Use high-quality Lanczos resampling for better upscaling
        img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Define enhanced enhancement levels based on quality setting
    enhancement_levels = {
        "Low": {
            "contrast": 1.25,
            "sharpness": 1.3,
            "color": 1.15,
            "brightness": 1.1
        },
        "Medium": {
            "contrast": 1.35,
            "sharpness": 1.5,
            "color": 1.25,
            "brightness": 1.15
        },
        "High": {
            "contrast": 1.45,
            "sharpness": 1.7,
            "color": 1.35,
            "brightness": 1.2
        }
    }
    
    # Get appropriate enhancement levels
    levels = enhancement_levels.get(quality, enhancement_levels["Medium"])
    
    # Check for image characteristics to apply adaptive processing
    # Convert to grayscale to analyze brightness and contrast
    try:
        gray_img = img.convert('L')
        img_array = np.array(gray_img)
        brightness = np.mean(img_array) / 255.0
        contrast = np.std(img_array) / 255.0
        
        # Adjust enhancement levels based on image characteristics
        if brightness < 0.4:  # Dark image
            levels["brightness"] *= 1.2
            levels["contrast"] *= 0.9
        elif brightness > 0.7:  # Bright image
            levels["brightness"] *= 0.9
            levels["contrast"] *= 1.1
            
        if contrast < 0.15:  # Low contrast image
            levels["contrast"] *= 1.3
    except:
        pass  # If analysis fails, use default levels
    
    # Advanced preprocessing - multiple stages of noise reduction and enhancement
    if quality != "Low":
        # Bilateral filter simulation for noise reduction while preserving edges
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=150, threshold=3))
    
    # Apply more advanced enhancement techniques for high quality
    if quality == "High":
        # Apply multiple passes of edge enhancement
        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        # Apply detail enhancement
        img = img.filter(ImageFilter.DETAIL)
        
        # Second pass of unsharp mask with different parameters
        img = img.filter(ImageFilter.UnsharpMask(radius=0.8, percent=250, threshold=2))
    
    # Apply contrast enhancement with auto-equalization
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(levels["contrast"])
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(levels["sharpness"])
    
    # Enhance color saturation
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(levels["color"])
    
    # Enhance brightness
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(levels["brightness"])
    
    return img

