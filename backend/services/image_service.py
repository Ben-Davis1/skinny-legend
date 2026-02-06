from PIL import Image
import os
from datetime import datetime
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_image(file, upload_dir):
    """Save and optimize an uploaded image"""
    if not allowed_file(file.filename):
        raise ValueError('Invalid file type')

    # Create unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{timestamp}{ext}"

    # Ensure upload directory exists
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, unique_filename)

    # Open and optimize image
    img = Image.open(file)

    # Convert RGBA to RGB if necessary
    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background

    # Resize if too large (max 1920px on longest side)
    max_size = 1920
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

    # Save with optimization
    img.save(filepath, quality=85, optimize=True)

    return unique_filename

def delete_image_file(filename, upload_dir):
    """Delete an image file"""
    filepath = os.path.join(upload_dir, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
