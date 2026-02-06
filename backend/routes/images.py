from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from database import query_db, execute_db
from services.image_service import save_uploaded_image, delete_image_file

bp = Blueprint('images', __name__, url_prefix='/api/images')

UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')

@bp.route('/upload', methods=['POST'])
def upload_image():
    """Upload one or more images as a group"""
    # Check if we have any files
    if not request.files:
        return jsonify({'error': 'No files provided'}), 400

    # Get all files with key 'images' or 'image'
    files = request.files.getlist('images') or [request.files.get('image')]
    files = [f for f in files if f and f.filename != '']

    if not files:
        return jsonify({'error': 'No valid files selected'}), 400

    user_id = request.form.get('user_id', 1)
    description = request.form.get('description', '')

    try:
        # Generate a group ID for these images
        group_id = str(uuid.uuid4())
        uploaded_images = []

        for idx, file in enumerate(files):
            # Save the image file
            image_path = save_uploaded_image(file, UPLOAD_DIR)

            # First image is primary
            is_primary = (idx == 0)

            # Save to database
            image_id = execute_db(
                '''INSERT INTO saved_images
                   (user_id, image_path, description, image_group_id, is_primary)
                   VALUES (?, ?, ?, ?, ?)''',
                [user_id, image_path, description if is_primary else '', group_id, is_primary]
            )

            image = query_db('SELECT * FROM saved_images WHERE id = ?', [image_id], one=True)
            uploaded_images.append(image)

        # Return the primary image with group info
        return jsonify({
            'primary_image': uploaded_images[0],
            'group_id': group_id,
            'total_images': len(uploaded_images),
            'all_images': uploaded_images
        }), 201

    except Exception as e:
        return jsonify({'error': f'Failed to upload images: {str(e)}'}), 500

@bp.route('', methods=['GET'])
def get_images():
    """Get all saved images grouped together"""
    user_id = request.args.get('user_id', 1)

    # Get all primary images
    primary_images = query_db(
        '''SELECT * FROM saved_images
           WHERE user_id = ? AND is_primary = 1
           ORDER BY created_at DESC''',
        [user_id]
    )

    # For each primary image, get its group members
    result = []
    for primary in primary_images:
        # Convert sqlite Row to dict
        primary_dict = dict(primary)
        group_id = primary_dict.get('image_group_id')

        if group_id:
            # Get all images in this group
            group_images = query_db(
                '''SELECT * FROM saved_images
                   WHERE image_group_id = ?
                   ORDER BY is_primary DESC, created_at''',
                [group_id]
            )
            # Convert to list of dicts
            primary_dict['group_images'] = [dict(img) for img in group_images]
            primary_dict['image_count'] = len(group_images)
        else:
            # Single image
            primary_dict['group_images'] = [primary_dict.copy()]
            primary_dict['image_count'] = 1

        result.append(primary_dict)

    return jsonify(result)

@bp.route('/<int:image_id>', methods=['GET'])
def get_image(image_id):
    """Get a specific image file"""
    image = query_db('SELECT * FROM saved_images WHERE id = ?', [image_id], one=True)

    if not image:
        return jsonify({'error': 'Image not found'}), 404

    image_path = os.path.join(UPLOAD_DIR, image['image_path'])
    if not os.path.exists(image_path):
        return jsonify({'error': 'Image file not found'}), 404

    return send_file(image_path)

@bp.route('/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """Delete an image (and all images in its group if it's primary)"""
    image = query_db('SELECT * FROM saved_images WHERE id = ?', [image_id], one=True)

    if not image:
        return jsonify({'error': 'Image not found'}), 404

    group_id = image['image_group_id']

    # If this is a primary image with a group, delete all images in the group
    if group_id and image['is_primary']:
        group_images = query_db(
            'SELECT * FROM saved_images WHERE image_group_id = ?',
            [group_id]
        )

        # Delete all files
        for img in group_images:
            delete_image_file(img['image_path'], UPLOAD_DIR)

        # Delete all from database
        execute_db('DELETE FROM saved_images WHERE image_group_id = ?', [group_id])

        return jsonify({'message': f'Deleted {len(group_images)} image(s)'}), 200
    else:
        # Just delete this single image
        delete_image_file(image['image_path'], UPLOAD_DIR)
        execute_db('DELETE FROM saved_images WHERE id = ?', [image_id])

        return jsonify({'message': 'Image deleted successfully'}), 200

@bp.route('/<int:image_id>/analyzed', methods=['PUT'])
def mark_analyzed(image_id):
    """Mark an image as analyzed"""
    execute_db('UPDATE saved_images SET analyzed = 1 WHERE id = ?', [image_id])
    image = query_db('SELECT * FROM saved_images WHERE id = ?', [image_id], one=True)
    return jsonify(image)
