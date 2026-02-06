from flask import Blueprint, request, jsonify
from database import query_db, execute_db
from routes.daily_logs import recalculate_daily_totals

bp = Blueprint('exercises', __name__, url_prefix='/api/exercises')

@bp.route('/<int:daily_log_id>', methods=['GET'])
def get_exercises(daily_log_id):
    """Get all exercises for a daily log"""
    exercises = query_db(
        'SELECT * FROM exercises WHERE daily_log_id = ? ORDER BY created_at',
        [daily_log_id]
    )
    return jsonify(exercises)

@bp.route('', methods=['POST'])
def create_exercise():
    """Create a new exercise entry"""
    data = request.json

    exercise_id = execute_db(
        '''INSERT INTO exercises
           (daily_log_id, exercise_type, duration_minutes, calories_burned, notes)
           VALUES (?, ?, ?, ?, ?)''',
        [
            data['daily_log_id'],
            data['exercise_type'],
            data['duration_minutes'],
            data.get('calories_burned', 0),
            data.get('notes', '')
        ]
    )

    # Recalculate total exercise minutes
    recalculate_exercise_totals(data['daily_log_id'])

    exercise = query_db('SELECT * FROM exercises WHERE id = ?', [exercise_id], one=True)
    return jsonify(exercise), 201

@bp.route('/<int:exercise_id>', methods=['PUT'])
def update_exercise(exercise_id):
    """Update an exercise entry"""
    data = request.json

    # Get the daily_log_id before updating
    old_exercise = query_db('SELECT daily_log_id FROM exercises WHERE id = ?', [exercise_id], one=True)

    execute_db(
        '''UPDATE exercises
           SET exercise_type = ?, duration_minutes = ?, calories_burned = ?, notes = ?
           WHERE id = ?''',
        [
            data['exercise_type'],
            data['duration_minutes'],
            data.get('calories_burned', 0),
            data.get('notes', ''),
            exercise_id
        ]
    )

    # Recalculate total exercise minutes
    if old_exercise:
        recalculate_exercise_totals(old_exercise['daily_log_id'])

    exercise = query_db('SELECT * FROM exercises WHERE id = ?', [exercise_id], one=True)
    return jsonify(exercise)

@bp.route('/<int:exercise_id>', methods=['DELETE'])
def delete_exercise(exercise_id):
    """Delete an exercise entry"""
    # Get the daily_log_id before deleting
    exercise = query_db('SELECT daily_log_id FROM exercises WHERE id = ?', [exercise_id], one=True)

    execute_db('DELETE FROM exercises WHERE id = ?', [exercise_id])

    # Recalculate total exercise minutes
    if exercise:
        recalculate_exercise_totals(exercise['daily_log_id'])

    return jsonify({'message': 'Exercise deleted successfully'}), 200

def recalculate_exercise_totals(daily_log_id):
    """Recalculate total exercise minutes for a daily log"""
    result = query_db(
        'SELECT SUM(duration_minutes) as total FROM exercises WHERE daily_log_id = ?',
        [daily_log_id],
        one=True
    )
    total_minutes = result['total'] if result['total'] else 0

    execute_db(
        'UPDATE daily_logs SET exercise_minutes = ? WHERE id = ?',
        [total_minutes, daily_log_id]
    )
    return total_minutes
