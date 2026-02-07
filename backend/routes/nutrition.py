from flask import Blueprint, request, jsonify
from database import query_db, execute_db

bp = Blueprint('nutrition', __name__, url_prefix='/api/nutrition')

@bp.route('/<date>', methods=['GET'])
def get_nutrition_breakdown(date):
    """Get complete nutrition breakdown for a date"""
    user_id = request.args.get('user_id', 1)

    # Get daily log
    daily_log = query_db(
        'SELECT * FROM daily_logs WHERE user_id = ? AND date = ?',
        [user_id, date],
        one=True
    )

    if not daily_log:
        return jsonify({'error': 'No log found for this date'}), 404

    # Get all food entries
    food_entries = query_db(
        'SELECT * FROM food_entries WHERE daily_log_id = ?',
        [daily_log['id']]
    )

    # Calculate macro totals
    totals = {
        'calories': 0,
        'protein_g': 0,
        'carbs_g': 0,
        'fat_g': 0,
        'fiber_g': 0,
        'sugar_g': 0
    }

    # Calculate micronutrient totals and track sources
    micro_totals = {
        'vitamin_a_mcg': 0,
        'vitamin_c_mg': 0,
        'vitamin_d_mcg': 0,
        'vitamin_e_mg': 0,
        'vitamin_k_mcg': 0,
        'vitamin_b6_mg': 0,
        'vitamin_b12_mcg': 0,
        'folate_mcg': 0,
        'calcium_mg': 0,
        'iron_mg': 0,
        'magnesium_mg': 0,
        'potassium_mg': 0,
        'zinc_mg': 0,
        'sodium_mg': 0
    }

    # Track sources for each micronutrient
    micro_sources = {key: [] for key in micro_totals.keys()}

    for entry in food_entries:
        totals['calories'] += entry['calories']
        totals['protein_g'] += entry['protein_g']
        totals['carbs_g'] += entry['carbs_g']
        totals['fat_g'] += entry['fat_g']
        totals['fiber_g'] += entry['fiber_g']
        totals['sugar_g'] += entry['sugar_g']

        # Get micronutrients for this entry
        micros = query_db(
            'SELECT * FROM micronutrients WHERE food_entry_id = ?',
            [entry['id']],
            one=True
        )

        if micros:
            for key in micro_totals.keys():
                amount = micros.get(key, 0)
                if amount > 0:
                    micro_totals[key] += amount
                    micro_sources[key].append({
                        'name': entry['name'],
                        'amount': round(amount, 1),
                        'type': 'food'
                    })

    # Add micronutrients from supplements
    supplements = query_db(
        'SELECT * FROM supplements WHERE daily_log_id = ?',
        [daily_log['id']]
    )

    for supplement in supplements:
        # Only add micronutrients that supplements track
        supplement_micros = ['vitamin_a_mcg', 'vitamin_c_mg', 'vitamin_d_mcg',
                           'calcium_mg', 'iron_mg', 'potassium_mg', 'sodium_mg']
        for key in supplement_micros:
            if key in micro_totals:
                amount = supplement.get(key, 0)
                if amount > 0:
                    micro_totals[key] += amount
                    micro_sources[key].append({
                        'name': supplement['name'],
                        'amount': round(amount, 1),
                        'type': 'supplement'
                    })

    return jsonify({
        'date': date,
        'daily_log': daily_log,
        'macros': totals,
        'micronutrients': micro_totals,
        'micronutrient_sources': micro_sources,
        'food_entries': food_entries
    })

@bp.route('/targets', methods=['GET'])
def get_vitamin_targets():
    """Get vitamin targets for user"""
    user_id = request.args.get('user_id', 1)

    targets = query_db(
        'SELECT * FROM vitamin_targets WHERE user_id = ?',
        [user_id]
    )

    return jsonify(targets)

@bp.route('/targets', methods=['POST'])
def set_vitamin_target():
    """Set a vitamin target"""
    data = request.json
    user_id = data.get('user_id', 1)

    # Use INSERT OR REPLACE to handle updates
    execute_db(
        '''INSERT OR REPLACE INTO vitamin_targets
           (user_id, nutrient_name, target_amount, unit)
           VALUES (?, ?, ?, ?)''',
        [user_id, data['nutrient_name'], data['target_amount'], data['unit']]
    )

    targets = query_db(
        'SELECT * FROM vitamin_targets WHERE user_id = ? AND nutrient_name = ?',
        [user_id, data['nutrient_name']],
        one=True
    )

    return jsonify(targets), 201

@bp.route('/targets/<int:target_id>', methods=['DELETE'])
def delete_vitamin_target(target_id):
    """Delete a vitamin target"""
    execute_db('DELETE FROM vitamin_targets WHERE id = ?', [target_id])
    return jsonify({'message': 'Target deleted successfully'}), 200

@bp.route('/history', methods=['GET'])
def get_nutrition_history():
    """Get nutrition history over a date range"""
    user_id = request.args.get('user_id', 1)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date are required'}), 400

    logs = query_db(
        '''SELECT * FROM daily_logs
           WHERE user_id = ? AND date BETWEEN ? AND ?
           ORDER BY date''',
        [user_id, start_date, end_date]
    )

    # Get food entries for each log
    history = []
    for log in logs:
        food_entries = query_db(
            'SELECT * FROM food_entries WHERE daily_log_id = ?',
            [log['id']]
        )

        # Calculate totals
        macro_totals = {
            'protein_g': sum(e['protein_g'] for e in food_entries),
            'carbs_g': sum(e['carbs_g'] for e in food_entries),
            'fat_g': sum(e['fat_g'] for e in food_entries),
            'fiber_g': sum(e['fiber_g'] for e in food_entries)
        }

        history.append({
            'date': log['date'],
            'total_calories': log['total_calories'],
            'calorie_goal': log.get('calorie_goal', 2000),
            'total_water_ml': log['total_water_ml'],
            'exercise_minutes': log['exercise_minutes'],
            'macros': macro_totals,
            'entry_count': len(food_entries)
        })

    return jsonify(history)
