from flask import Blueprint, request, jsonify
from database import query_db, execute_db
from datetime import datetime
from services.calculations import calculate_bmr, calculate_tdee, calculate_calorie_goal, calculate_macro_targets

bp = Blueprint('daily_logs', __name__, url_prefix='/api/daily-logs')

def get_current_targets(user_id):
    """Get current calorie and macro targets from user profile (uses custom if set)"""
    profile = query_db(
        'SELECT * FROM user_profile WHERE user_id = ?',
        [user_id],
        one=True
    )

    if not profile:
        # Return defaults if no profile
        return {
            'calorie_goal': 2000,
            'protein_target_g': 150,
            'carbs_target_g': 200,
            'fat_target_g': 70
        }

    # Check if using custom targets
    if profile.get('use_custom_targets'):
        # Use custom values if set
        return {
            'calorie_goal': profile.get('custom_calorie_goal') or round(calculate_calorie_goal(profile['tdee'], profile['goal'])),
            'protein_target_g': profile.get('custom_protein_target_g') or profile['protein_target_g'],
            'carbs_target_g': profile.get('custom_carbs_target_g') or profile['carbs_target_g'],
            'fat_target_g': profile.get('custom_fat_target_g') or profile['fat_target_g']
        }
    else:
        # Use auto-calculated values
        calorie_goal = calculate_calorie_goal(profile['tdee'], profile['goal'])
        return {
            'calorie_goal': round(calorie_goal),
            'protein_target_g': profile['protein_target_g'],
            'carbs_target_g': profile['carbs_target_g'],
            'fat_target_g': profile['fat_target_g']
        }

@bp.route('', methods=['GET'])
def get_all_logs():
    """Get all daily logs"""
    user_id = request.args.get('user_id', 1)
    logs = query_db(
        'SELECT * FROM daily_logs WHERE user_id = ? ORDER BY date DESC',
        [user_id]
    )
    return jsonify(logs)

@bp.route('/<date>', methods=['GET'])
def get_log_by_date(date):
    """Get or create a daily log for a specific date"""
    user_id = request.args.get('user_id', 1)

    # Try to get existing log
    log = query_db(
        'SELECT * FROM daily_logs WHERE user_id = ? AND date = ?',
        [user_id, date],
        one=True
    )

    # If no log exists, create one with current targets
    if not log:
        targets = get_current_targets(user_id)
        log_id = execute_db(
            '''INSERT INTO daily_logs
               (user_id, date, calorie_goal, protein_target_g, carbs_target_g, fat_target_g)
               VALUES (?, ?, ?, ?, ?, ?)''',
            [user_id, date, targets['calorie_goal'], targets['protein_target_g'],
             targets['carbs_target_g'], targets['fat_target_g']]
        )
        log = query_db(
            'SELECT * FROM daily_logs WHERE id = ?',
            [log_id],
            one=True
        )

    return jsonify(log)

@bp.route('', methods=['POST'])
def create_log():
    """Create a new daily log"""
    data = request.json
    user_id = data.get('user_id', 1)
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))

    targets = get_current_targets(user_id)

    log_id = execute_db(
        '''INSERT INTO daily_logs
           (user_id, date, total_water_ml, exercise_minutes, notes,
            calorie_goal, protein_target_g, carbs_target_g, fat_target_g)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        [user_id, date, data.get('total_water_ml', 0), data.get('exercise_minutes', 0),
         data.get('notes', ''), targets['calorie_goal'], targets['protein_target_g'],
         targets['carbs_target_g'], targets['fat_target_g']]
    )

    log = query_db('SELECT * FROM daily_logs WHERE id = ?', [log_id], one=True)
    return jsonify(log), 201

@bp.route('/<int:log_id>', methods=['PUT'])
def update_log(log_id):
    """Update a daily log"""
    data = request.json

    execute_db(
        '''UPDATE daily_logs
           SET total_water_ml = ?, exercise_minutes = ?, notes = ?
           WHERE id = ?''',
        [data.get('total_water_ml'), data.get('exercise_minutes'), data.get('notes'), log_id]
    )

    log = query_db('SELECT * FROM daily_logs WHERE id = ?', [log_id], one=True)
    return jsonify(log)

@bp.route('/<int:log_id>', methods=['DELETE'])
def delete_log(log_id):
    """Delete a daily log"""
    execute_db('DELETE FROM daily_logs WHERE id = ?', [log_id])
    return jsonify({'message': 'Log deleted successfully'}), 200

def recalculate_daily_totals(daily_log_id):
    """Recalculate total calories for a daily log"""
    result = query_db(
        'SELECT SUM(calories) as total FROM food_entries WHERE daily_log_id = ?',
        [daily_log_id],
        one=True
    )
    total_calories = result['total'] if result['total'] else 0

    execute_db(
        'UPDATE daily_logs SET total_calories = ? WHERE id = ?',
        [total_calories, daily_log_id]
    )
    return total_calories
