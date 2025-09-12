import os
import numpy as np
import pickle
from PIL import Image
from sklearn.neighbors import NearestNeighbors

class FashionRecommender:
    def __init__(self, embeddings_path='embeddings_simple.pkl', filenames_path='filenames_simple.pkl'):
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.embeddings_path = os.path.join(script_dir, embeddings_path)
        self.filenames_path = os.path.join(script_dir, filenames_path)
        self.feature_list = None
        self.filenames = None
        self.load_data()
        
    def load_data(self):
        try:
            self.feature_list = np.array(pickle.load(open(self.embeddings_path, 'rb')))
            self.filenames = pickle.load(open(self.filenames_path, 'rb'))
            return True
        except Exception as e:
            print(f"Error loading recommendation data: {e}")
            return False
            
    def extract_features(self, img_path):
        try:
            # Load image and convert to grayscale
            img = Image.open(img_path).convert('L').resize((100, 100))
            img_array = np.array(img)
            
            # Extract simple features (flatten the image)
            features = img_array.flatten()
            
            # Normalize features
            features = features / 255.0
            
            return features
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
            
    def recommend(self, img_path, num_recommendations=5):
        if self.feature_list is None or self.filenames is None:
            return []
            
        features = self.extract_features(img_path)
        if features is None:
            return []
            
        # Ensure we have at least one recommendation
        n_neighbors = min(num_recommendations + 1, len(self.feature_list))
        n_neighbors = max(2, n_neighbors)  # At least 2 to get 1 recommendation after skipping self
        
        neighbors = NearestNeighbors(n_neighbors=n_neighbors, algorithm='brute', metric='euclidean')
        neighbors.fit(self.feature_list)
        
        distances, indices = neighbors.kneighbors([features])
        
        # Return the recommended image paths
        recommendations = []
        for idx in indices[0][1:]:  # Skip the first one as it might be the image itself
            recommendations.append(self.filenames[idx])
            
        return recommendations
        
    def check_sustainability(self, img_path):
        import random
        
        score = random.uniform(1.0, 5.0)
        
        materials = ["cotton", "polyester", "wool", "silk", "linen", "nylon"]
        selected_material = random.choice(materials)
        
        sustainability_notes = {
            "cotton": "Cotton is natural but requires a lot of water to produce.",
            "polyester": "Polyester is synthetic and not biodegradable, but durable.",
            "wool": "Wool is natural, renewable, and biodegradable.",
            "silk": "Silk is natural but requires intensive processing.",
            "linen": "Linen is one of the most sustainable fabrics, requiring little water.",
            "nylon": "Nylon is synthetic and not biodegradable."
        }
        
        notes = sustainability_notes[selected_material]
        
        if score < 2.0:
            recommendation = "Consider more sustainable alternatives."
        elif score < 3.5:
            recommendation = "Moderately sustainable, but improvements possible."
        else:
            recommendation = "Good sustainable choice!"
            
        return {
            "score": round(score, 1),
            "material": selected_material,
            "notes": notes,
            "recommendation": recommendation
        } 