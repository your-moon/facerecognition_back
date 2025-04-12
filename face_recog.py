import face_recognition
import cv2
import numpy as np
import os
import pickle
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

class FaceEncodingCache:
    def __init__(self, cache_file: str = "face_encodings_cache.pkl"):
        self.cache_file = cache_file
        self.cache = {}
        self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    self.cache = pickle.load(f)
            except:
                self.cache = {}

    def save_cache(self):
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)

    def get_encoding(self, image_path: str) -> Tuple[List[np.ndarray], float]:
        current_time = datetime.now()
        if image_path in self.cache:
            encodings, timestamp = self.cache[image_path]
            # Check if cache is not older than 24 hours
            if current_time - timestamp < timedelta(hours=24):
                return encodings
        return None

    def set_encoding(self, image_path: str, encodings: List[np.ndarray]):
        self.cache[image_path] = (encodings, datetime.now())
        self.save_cache()

# Global cache instance
face_cache = FaceEncodingCache()

def process_image(image_path: str, max_size: int = 1024) -> np.ndarray:
    """
    Process image for faster face recognition by resizing if too large
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    height, width = image.shape[:2]
    if max(height, width) > max_size:
        scale = max_size / max(height, width)
        image = cv2.resize(image, (int(width * scale), int(height * scale)))
    
    # Convert BGR to RGB
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def load_known_faces(faces_directory: str = "faces") -> Tuple[List[str], List[np.ndarray]]:
    """
    Load all face images from the faces directory with caching support.
    """
    known_face_encodings = []
    known_face_names = []
    
    if not os.path.exists(faces_directory):
        raise FileNotFoundError(f"Faces directory '{faces_directory}' not found")
    
    for person_name in os.listdir(faces_directory):
        person_dir = os.path.join(faces_directory, person_name)
        
        if not os.path.isdir(person_dir):
            continue
            
        person_encodings = []
        for filename in os.listdir(person_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                image_path = os.path.join(person_dir, filename)
                try:
                    # Check cache first
                    cached_encodings = face_cache.get_encoding(image_path)
                    if cached_encodings is not None:
                        person_encodings.extend(cached_encodings)
                        continue

                    # Process and encode if not in cache
                    face_image = process_image(image_path)
                    face_encodings = face_recognition.face_encodings(face_image)
                    
                    if face_encodings:
                        face_cache.set_encoding(image_path, face_encodings)
                        person_encodings.extend(face_encodings)
                except Exception as e:
                    print(f"Warning: Error processing {image_path}: {str(e)}")
                    continue
        
        if person_encodings:
            for encoding in person_encodings:
                known_face_encodings.append(encoding)
                known_face_names.append(person_name)
                
    return known_face_names, known_face_encodings

def find_faces(input_image_path: str, faces_directory: str = "faces", tolerance: float = 0.6) -> List[Dict]:
    """
    Find and compare faces with optimized processing.
    """
    known_face_names, known_face_encodings = load_known_faces(faces_directory)
    
    if not known_face_encodings:
        return []
    
    try:
        # Process input image with size limit
        input_image = process_image(input_image_path)
        
        # Use batch face detection for better performance
        input_face_locations = face_recognition.face_locations(input_image, model="cnn" if cv2.cuda.getCudaEnabledDeviceCount() > 0 else "hog")
        input_face_encodings = face_recognition.face_encodings(input_image, input_face_locations)
        
        results = []
        
        # Batch process face comparisons
        for face_encoding, face_location in zip(input_face_encodings, input_face_locations):
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=tolerance)
            
            if True in matches:
                best_match_index = np.argmin(face_distances)
                confidence = float(1 - face_distances[best_match_index])
                
                match_result = {
                    "name": known_face_names[best_match_index],
                    "confidence": confidence,
                    "location": {
                        "top": face_location[0],
                        "right": face_location[1],
                        "bottom": face_location[2],
                        "left": face_location[3]
                    },
                    "matched": True
                }
            else:
                match_result = {
                    "name": "Unknown",
                    "confidence": 0.0,
                    "location": {
                        "top": face_location[0],
                        "right": face_location[1],
                        "bottom": face_location[2],
                        "left": face_location[3]
                    },
                    "matched": False
                }
            
            results.append(match_result)
        
        return results
    
    except Exception as e:
        raise Exception(f"Error processing input image: {str(e)}")

if __name__ == "__main__":
    try:
        results = find_faces("test.jpg")
        for result in results:
            if result["matched"]:
                print(f"Found {result['name']} with {result['confidence']:.2%} confidence")
            else:
                print("Found unknown face")
    except Exception as e:
        print(f"Error: {str(e)}")