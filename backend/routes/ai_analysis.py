from flask import Blueprint, request, jsonify
import os
from database import query_db, execute_db
from services.ai_service import analyze_food_image

bp = Blueprint('ai_analysis', __name__, url_prefix='/api/ai')

UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')

@bp.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Analyze food image(s) using AI - automatically uses all images in group"""
    data = request.json
    image_id = data.get('image_id')
    custom_notes = data.get('notes', '')  # Custom instructions from user
    force_reanalyze = data.get('force_reanalyze', False)

    if not image_id:
        return jsonify({'error': 'image_id is required'}), 400

    # Get primary image from database
    image = query_db('SELECT * FROM saved_images WHERE id = ?', [image_id], one=True)

    if not image:
        return jsonify({'error': 'Image not found'}), 404

    group_id = image['image_group_id']

    # Check if we have a previous analysis (only if not forced)
    if image['analysis_result'] and not force_reanalyze:
        import json
        try:
            previous_result = json.loads(image['analysis_result'])
            previous_result['is_cached'] = True
            return jsonify(previous_result)
        except:
            pass  # If parsing fails, continue with new analysis

    # Get full image path for primary image
    image_path = os.path.join(UPLOAD_DIR, image['image_path'])

    if not os.path.exists(image_path):
        return jsonify({'error': 'Image file not found'}), 404

    # Get all additional images in the group
    additional_image_paths = []
    if group_id:
        group_images = query_db(
            '''SELECT * FROM saved_images
               WHERE image_group_id = ? AND id != ? AND is_primary = 0
               ORDER BY created_at''',
            [group_id, image_id]
        )

        for img in group_images:
            img_path = os.path.join(UPLOAD_DIR, img['image_path'])
            if os.path.exists(img_path):
                additional_image_paths.append(img_path)

    try:
        # Analyze image(s) - pass additional images if they exist
        result = analyze_food_image(
            image_path,
            custom_notes,
            additional_image_paths if additional_image_paths else None
        )

        # Save analysis result to primary image
        import json
        result_json = json.dumps(result)
        execute_db(
            'UPDATE saved_images SET analyzed = 1, analysis_result = ? WHERE id = ?',
            [result_json, image_id]
        )

        # Mark all images in group as analyzed
        if group_id:
            execute_db(
                'UPDATE saved_images SET analyzed = 1 WHERE image_group_id = ?',
                [group_id]
            )

        result['is_cached'] = False
        result['images_analyzed'] = 1 + len(additional_image_paths)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/calculate-goals', methods=['POST'])
def calculate_goals():
    """Calculate personalized calorie goals using AI"""
    from services.calculations import calculate_bmr, calculate_tdee, calculate_calorie_goal

    data = request.json

    try:
        bmr = calculate_bmr(
            data['weight_kg'],
            data['height_cm'],
            data['age'],
            data['gender']
        )

        tdee = calculate_tdee(bmr, data['activity_level'])

        calorie_goal = calculate_calorie_goal(tdee, data['goal'])

        return jsonify({
            'bmr': round(bmr),
            'tdee': round(tdee),
            'calorie_goal': round(calorie_goal),
            'goal': data['goal']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
