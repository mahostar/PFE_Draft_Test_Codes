import sys
import os
import boto3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# S3 configuration
S3_ENDPOINT = "https://qlfmomqqbmusdvxycwhw.supabase.co/storage/v1/s3"
S3_ACCESS_KEY = "e11f7229ad642e4750a0270114d23c5c"
S3_SECRET_KEY = "7091f5079ad777aa2c71a998ee593a565219f7abf4f148779f4c5f1ecfce5836"
S3_REGION = "eu-west-3"
BUCKET_NAME = "test"

def get_encryption_key(password: str) -> bytes:
    """Generate encryption key from password"""
    salt = b'supabase_salt'  # You might want to store this securely
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_file(file_path: str, password: str) -> str:
    """Encrypt file and save it with .encrypted extension"""
    # Generate key from password
    key = get_encryption_key(password)
    f = Fernet(key)
    
    # Read and encrypt file
    with open(file_path, 'rb') as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    
    # Save encrypted file
    encrypted_path = file_path + '.encrypted'
    with open(encrypted_path, 'wb') as file:
        file.write(encrypted_data)
    
    return encrypted_path

def upload_to_storage(file_path: str) -> dict:
    """Upload file using S3 client"""
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION
        )
        
        # Get the file name from the path
        file_name = os.path.basename(file_path)
        
        # Upload the file
        with open(file_path, 'rb') as f:
            s3_client.upload_fileobj(
                f,
                BUCKET_NAME,
                file_name
            )
        
        # Generate the public URL for the uploaded file
        file_url = f"https://qlfmomqqbmusdvxycwhw.supabase.co/storage/v1/object/public/{BUCKET_NAME}/{file_name}"
        return {"success": True, "message": f"File {file_name} uploaded successfully", "url": file_url}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    # Get file path and password from user
    file_path = input("Enter the file path: ")
    password = input("Enter encryption password: ")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist")
        sys.exit(1)
    
    # Encrypt the file
    print("Encrypting file...")
    encrypted_file_path = encrypt_file(file_path, password)
    
    # Upload the encrypted file
    print(f"Uploading encrypted file...")
    result = upload_to_storage(encrypted_file_path)
    
    # Clean up the encrypted file
    os.remove(encrypted_file_path)
    
    if result["success"]:
        print("✅ Upload successful!")
        print(f"🔗 File URL: {result['url']}")
    else:
        print(f"❌ Upload failed: {result.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main() 