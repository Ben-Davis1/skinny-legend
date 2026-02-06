from flask import Blueprint, request, jsonify
from database import query_db, execute_db
from services.ai_service import estimate_supplement_micronutrients

bp = Blueprint('supplements', __name__, url_prefix='/api/supplements')

@bp.route('/<int:daily_log_id>', methods=['GET'])
def get_supplements(daily_log_id):
    """Get all supplements for a daily log"""
    supplements = query_db(
        'SELECT * FROM supplements WHERE daily_log_id = ? ORDER BY created_at',
        [daily_log_id]
    )
    return jsonify(supplements)

@bp.route('/recent', methods=['GET'])
def get_recent_supplements():
    """Get recently used supplements (last 30 days, unique by name)"""
    user_id = request.args.get('user_id', 1)

    supplements = query_db(
        '''SELECT s.* FROM supplements s
           JOIN daily_logs dl ON s.daily_log_id = dl.id
           WHERE dl.user_id = ? AND dl.date >= date('now', '-30 days')
           ORDER BY s.created_at DESC
           LIMIT 50''',
        [user_id]
    )
    return jsonify(supplements)

@bp.route('', methods=['POST'])
def create_supplement():
    """Create a new supplement entry"""
    data = request.json

    # Estimate micronutrients from supplement name and dosage
    micros = estimate_supplement_micronutrients(
        data['name'],
        data.get('dosage', '')
    )

    supplement_id = execute_db(
        '''INSERT INTO supplements
           (daily_log_id, name, dosage, type, time_taken, notes,
            vitamin_a_mcg, vitamin_c_mg, vitamin_d_mcg, calcium_mg,
            iron_mg, potassium_mg, sodium_mg)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        [
            data['daily_log_id'],
            data['name'],
            data.get('dosage', ''),
            data.get('type', 'supplement'),
            data.get('time_taken', ''),
            data.get('notes', ''),
            micros.get('vitamin_a_mcg', 0),
            micros.get('vitamin_c_mg', 0),
            micros.get('vitamin_d_mcg', 0),
            micros.get('calcium_mg', 0),
            micros.get('iron_mg', 0),
            micros.get('potassium_mg', 0),
            micros.get('sodium_mg', 0)
        ]
    )

    supplement = query_db('SELECT * FROM supplements WHERE id = ?', [supplement_id], one=True)
    return jsonify(supplement), 201

@bp.route('/<int:supplement_id>', methods=['PUT'])
def update_supplement(supplement_id):
    """Update a supplement entry"""
    data = request.json

    execute_db(
        '''UPDATE supplements
           SET name = ?, dosage = ?, type = ?, time_taken = ?, notes = ?
           WHERE id = ?''',
        [
            data['name'],
            data.get('dosage', ''),
            data.get('type', 'supplement'),
            data.get('time_taken', ''),
            data.get('notes', ''),
            supplement_id
        ]
    )

    supplement = query_db('SELECT * FROM supplements WHERE id = ?', [supplement_id], one=True)
    return jsonify(supplement)

@bp.route('/<int:supplement_id>', methods=['DELETE'])
def delete_supplement(supplement_id):
    """Delete a supplement entry"""
    execute_db('DELETE FROM supplements WHERE id = ?', [supplement_id])
    return jsonify({'message': 'Supplement deleted successfully'}), 200
