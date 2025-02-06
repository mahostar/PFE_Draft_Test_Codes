import os
import boto3
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# S3 configuration
S3_ENDPOINT = "https://qlfmomqqbmusdvxycwhw.supabase.co/storage/v1/s3"
S3_ACCESS_KEY = "e11f7229ad642e4750a0270114d23c5c"
S3_SECRET_KEY = "7091f5079ad777aa2c71a998ee593a565219f7abf4f148779f4c5f1ecfce5836"
S3_REGION = "eu-west-3"
BUCKET_NAME = "test"
DOWNLOAD_DIR = r"C:\Users\Mohamed\Desktop\project pfe\supabase_encryption\down"

def derive_key(password: str, salt: bytes) -> tuple[bytes, bytes]:
    """Generate a 256-bit key from password using PBKDF2"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 32 bytes = 256 bits
        salt=salt,
        iterations=100000,
    )
    key = kdf.derive(password.encode())
    return key, salt

def decrypt_file(file_path: str, password: str) -> str:
    """Decrypt file using AES-256 in CBC mode"""
    # Read the encrypted file
    with open(file_path, 'rb') as file:
        data = file.read()
    
    # Extract salt, IV, and encrypted data
    salt = data[:16]
    iv = data[16:32]
    encrypted_data = data[32:]
    
    # Derive key using the same salt
    key, _ = derive_key(password, salt)
    
    # Create AES cipher in CBC mode
    cipher = Cipher(algorithms.AES256(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    
    try:
        # Decrypt the data
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Create unpadder
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        # Save decrypted file
        decrypted_path = file_path.replace('.aes256', '')
        with open(decrypted_path, 'wb') as file:
            file.write(data)
        
        return decrypted_path
    
    except Exception as e:
        print("❌ Decryption failed. Wrong password or corrupted file.")
        raise e

def list_bucket_files():
    """List all files in the bucket"""
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION
        )
        
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' not in response:
            return []
        
        # Only show .aes256 files
        return [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.aes256')]
    except Exception as e:
        print(f"❌ Error listing files: {str(e)}")
        return []

def download_file(file_name: str) -> str:
    """Download file from bucket"""
    try:
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        
        s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION
        )
        
        download_path = os.path.join(DOWNLOAD_DIR, file_name)
        s3_client.download_file(BUCKET_NAME, file_name, download_path)
        return download_path
    
    except Exception as e:
        print(f"❌ Download failed: {str(e)}")
        raise e

def main():
    # List all files
    print("📁 AES-256 encrypted files in bucket:")
    files = list_bucket_files()
    if not files:
        print("No encrypted files found in bucket")
        return
    
    # Display files with numbers
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    
    # Get user selection
    while True:
        try:
            selection = int(input("\nSelect file number to download: "))
            if 1 <= selection <= len(files):
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    selected_file = files[selection - 1]
    
    # Get password
    password = input("Enter decryption password: ")
    
    try:
        # Download encrypted file
        print(f"\nDownloading {selected_file}...")
        downloaded_path = download_file(selected_file)
        
        # Decrypt file
        print("Decrypting file using AES-256...")
        decrypted_path = decrypt_file(downloaded_path, password)
        
        # Clean up encrypted file
        os.remove(downloaded_path)
        
        print(f"✅ File successfully decrypted and saved to: {decrypted_path}")
    
    except Exception as e:
        print(f"❌ Operation failed: {str(e)}")

if __name__ == "__main__":
    main() 