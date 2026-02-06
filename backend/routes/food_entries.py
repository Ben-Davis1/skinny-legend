from flask import Blueprint, request, jsonify
from database import query_db, execute_db
from routes.daily_logs import recalculate_daily_totals
from services.ai_service import estimate_micronutrients

bp = Blueprint('food_entries', __name__, url_prefix='/api/food-entries')

@bp.route('/<int:daily_log_id>', methods=['GET'])
def get_entries(daily_log_id):
    """Get all food entries for a daily log"""
    entries = query_db(
        'SELECT * FROM food_entries WHERE daily_log_id = ? ORDER BY created_at',
        [daily_log_id]
    )
    return jsonify(entries)

@bp.route('', methods=['POST'])
def create_entry():
    """Create a new food entry"""
    data = request.json

    entry_id = execute_db(
        '''INSERT INTO food_entries
           (daily_log_id, name, calories, protein_g, carbs_g, fat_g, fiber_g, sugar_g,
            meal_type, image_path, barcode, serving_size)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        [
            data['daily_log_id'],
            data['name'],
            data['calories'],
            data.get('protein_g', 0),
            data.get('carbs_g', 0),
            data.get('fat_g', 0),
            data.get('fiber_g', 0),
            data.get('sugar_g', 0),
            data.get('meal_type'),
            data.get('image_path'),
            data.get('barcode'),
            data.get('serving_size', '1 serving')
        ]
    )

    # Get or estimate micronutrients
    if 'micronutrients' in data and data['micronutrients']:
        micro = data['micronutrients']
    else:
        # Estimate micronutrients using AI
        micro = estimate_micronutrients(
            data['name'],
            data['calories'],
            data.get('protein_g', 0),
            data.get('carbs_g', 0),
            data.get('fat_g', 0)
        )

    # Insert micronutrients
    execute_db(
        '''INSERT INTO micronutrients
           (food_entry_id, vitamin_a_mcg, vitamin_c_mg, vitamin_d_mcg, vitamin_e_mg,
            vitamin_k_mcg, vitamin_b6_mg, vitamin_b12_mcg, folate_mcg, calcium_mg,
            iron_mg, magnesium_mg, potassium_mg, zinc_mg, sodium_mg)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        [
            entry_id,
            micro.get('vitamin_a_mcg', 0),
            micro.get('vitamin_c_mg', 0),
            micro.get('vitamin_d_mcg', 0),
            micro.get('vitamin_e_mg', 0),
            micro.get('vitamin_k_mcg', 0),
            micro.get('vitamin_b6_mg', 0),
            micro.get('vitamin_b12_mcg', 0),
            micro.get('folate_mcg', 0),
            micro.get('calcium_mg', 0),
            micro.get('iron_mg', 0),
            micro.get('magnesium_mg', 0),
            micro.get('potassium_mg', 0),
            micro.get('zinc_mg', 0),
            micro.get('sodium_mg', 0)
        ]
    )

    # Recalculate daily totals
    recalculate_daily_totals(data['daily_log_id'])

    entry = query_db('SELECT * FROM food_entries WHERE id = ?', [entry_id], one=True)
    return jsonify(entry), 201

@bp.route('/<int:entry_id>', methods=['PUT'])
def update_entry(entry_id):
    """Update a food entry"""
    data = request.json

    # Get the daily_log_id before updating
    old_entry = query_db('SELECT daily_log_id FROM food_entries WHERE id = ?', [entry_id], one=True)

    execute_db(
        '''UPDATE food_entries
           SET name = ?, calories = ?, protein_g = ?, carbs_g = ?, fat_g = ?,
               fiber_g = ?, sugar_g = ?, meal_type = ?, serving_size = ?
           WHERE id = ?''',
        [
            data['name'],
            data['calories'],
            data.get('protein_g', 0),
            data.get('carbs_g', 0),
            data.get('fat_g', 0),
            data.get('fiber_g', 0),
            data.get('sugar_g', 0),
            data.get('meal_type'),
            data.get('serving_size', '1 serving'),
            entry_id
        ]
    )

    # Recalculate daily totals
    if old_entry:
        recalculate_daily_totals(old_entry['daily_log_id'])

    entry = query_db('SELECT * FROM food_entries WHERE id = ?', [entry_id], one=True)
    return jsonify(entry)

@bp.route('/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    """Delete a food entry"""
    # Get the daily_log_id before deleting
    entry = query_db('SELECT daily_log_id FROM food_entries WHERE id = ?', [entry_id], one=True)

    execute_db('DELETE FROM food_entries WHERE id = ?', [entry_id])

    # Recalculate daily totals
    if entry:
        recalculate_daily_totals(entry['daily_log_id'])

    return jsonify({'message': 'Entry deleted successfully'}), 200

@bp.route('/recent', methods=['GET'])
def get_recent_foods():
    """Get recently used unique foods"""
    user_id = request.args.get('user_id', 1)
    limit = int(request.args.get('limit', 20))

    # Get distinct foods ordered by most recent use
    foods = query_db(
        '''SELECT
               name,
               calories,
               protein_g,
               carbs_g,
               fat_g,
               fiber_g,
               sugar_g,
               serving_size,
               MAX(created_at) as last_used
           FROM food_entries
           WHERE daily_log_id IN (
               SELECT id FROM daily_logs WHERE user_id = ?
           )
           GROUP BY LOWER(name)
           ORDER BY last_used DESC
           LIMIT ?''',
        [user_id, limit]
    )

    return jsonify(foods)
