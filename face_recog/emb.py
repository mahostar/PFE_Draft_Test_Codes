import cv2
import numpy as np
from insightface.app import FaceAnalysis
import os

def generate_embedding(image_path):
    # Initialize Face Recognition model optimized for Jetson Nano
    app = FaceAnalysis(name="buffalo_l", 
                      providers=['CPUExecutionProvider'])  # Jetson Nano optimization
    app.prepare(ctx_id=0, det_size=(640, 640))

    # Load the image containing the known face
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    known_img = cv2.imread(image_path)
    if known_img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Detect face and extract embedding
    faces = app.get(known_img)

    if not faces:
        raise ValueError("No face detected in the image. Please use a clearer image.")

    if len(faces) > 1:
        print("Warning: Multiple faces detected. Using the most prominent face.")

    # Get the face with highest detection score
    face = max(faces, key=lambda x: x.det_score)
    embedding = face.normed_embedding

    # Save the embedding
    output_file = "known_face_embedding.npy"
    np.save(output_file, embedding)
    
    print(f"✅ Face embedding successfully generated and saved to {output_file}")
    print(f"📊 Detection confidence score: {face.det_score:.2f}")
    
    # Draw face rectangle on image and save it for verification
    x1, y1, x2, y2 = map(int, face.bbox)
    cv2.rectangle(known_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(known_img, "Detected Face", (x1, y1-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    # Save annotated image
    cv2.imwrite("face_detection_result.jpg", known_img)
    print("✅ Verification image saved as 'face_detection_result.jpg'")

if __name__ == "__main__":
    try:
        image_path = "known_face.jpg"
        generate_embedding(image_path)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
