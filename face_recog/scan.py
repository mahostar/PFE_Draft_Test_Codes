import cv2
import numpy as np
from insightface.app import FaceAnalysis
import time
import os

class FaceRecognizer:
    def __init__(self, embedding_path="known_face_embedding.npy", threshold=0.5):
        self.threshold = threshold
        
        # Load the known face embedding
        if not os.path.exists(embedding_path):
            raise FileNotFoundError(f"Embedding file not found: {embedding_path}")
        self.known_embedding = np.load(embedding_path)
        
        # Initialize Face Recognition model for Jetson Nano
        self.app = FaceAnalysis(name="buffalo_l", 
                              providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
    def compare_face(self, face_embedding):
        """Compare face embedding with stored embedding"""
        similarity = np.dot(self.known_embedding, face_embedding)
        return similarity > self.threshold, similarity
    
    def process_frame(self, frame):
        """Process a single frame and return the annotated frame"""
        faces = self.app.get(frame)
        
        for face in faces:
            # Get face location
            x1, y1, x2, y2 = map(int, face.bbox)
            
            # Compare with known face
            is_match, similarity = self.compare_face(face.normed_embedding)
            
            # Draw results
            color = (0, 255, 0) if is_match else (0, 0, 255)
            label = f"Known Face ({similarity:.2f})" if is_match else f"Unknown ({similarity:.2f})"
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        
        return frame, any(self.compare_face(face.normed_embedding)[0] for face in faces)

def scan_image(image_path):
    """Scan a single image for face recognition"""
    recognizer = FaceRecognizer()
    
    # Read image
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    # Process image
    processed_image, found_match = recognizer.process_frame(image)
    
    # Save result
    output_path = "recognition_result.jpg"
    cv2.imwrite(output_path, processed_image)
    
    return found_match, output_path

def scan_video(duration=10):
    """Scan video feed for face recognition"""
    recognizer = FaceRecognizer()
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open video capture device")
    
    print(f"👁️ Scanning video feed for {duration} seconds...")
    start_time = time.time()
    found_match = False
    
    try:
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Process frame
            processed_frame, frame_match = recognizer.process_frame(frame)
            found_match = found_match or frame_match
            
            # Display frame
            cv2.imshow("Face Recognition", processed_frame)
            
            # Break if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    return found_match

if __name__ == "__main__":
    try:
        # Uncomment the mode you want to use:
        
        # Image mode
        result, output_path = scan_image("known_face1.jpg")
        print(f"{'✅ Face recognized!' if result else '❌ No known face detected!'}")
        print(f"Result saved to: {output_path}")
        
        # Video mode
        #result = scan_video(duration=10)
        #print(f"{'✅ Face recognized!' if result else '❌ No known face detected!'}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")