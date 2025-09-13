#!/usr/bin/env python3
import os
import pickle
import numpy as np
from PIL import Image
import glob

# Simple feature generation function
def generate_simple_features(image_paths):
    features = []
    filenames = []
    
    for img_path in image_paths[:100]:  # Limit to first 100 images for speed
        try:
            img = Image.open(img_path).convert('L')  # Convert to grayscale
            img = img.resize((224, 224))  # Resize to standard size
            img_array = np.array(img).flatten()  # Flatten to 1D
            features.append(img_array)
            filenames.append(os.path.basename(img_path))
        except Exception as e:
            print(f'Error processing {img_path}: {e}')
            continue
    
    return np.array(features), filenames

# Get image files
image_files = glob.glob('images/*.jpg')[:100]  # Limit to 100 images
print(f'Found {len(image_files)} images')

if len(image_files) > 0:
    features, filenames = generate_simple_features(image_files)
    
    # Save features
    with open('embeddings_simple.pkl', 'wb') as f:
        pickle.dump(features, f)
    
    with open('filenames_simple.pkl', 'wb') as f:
        pickle.dump(filenames, f)
    
    print(f'Generated pickle files with {len(filenames)} images')
else:
    print('No images found, creating empty pickle files')
    # Create empty files
    with open('embeddings_simple.pkl', 'wb') as f:
        pickle.dump(np.array([]), f)
    
    with open('filenames_simple.pkl', 'wb') as f:
        pickle.dump([], f)

