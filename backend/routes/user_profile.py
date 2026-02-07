from flask import Blueprint, request, jsonify
from database import query_db, execute_db
from services.calculations import calculate_bmr, calculate_tdee, calculate_calorie_goal, calculate_macro_targets, calculate_water_target, get_rda_targets

bp = Blueprint('user_profile', __name__, url_prefix='/api/profile')

@bp.route('', methods=['GET'])
def get_profile():
    """Get user profile"""
    user_id = request.args.get('user_id', 1)

    profile = query_db(
        'SELECT * FROM user_profile WHERE user_id = ?',
        [user_id],
        one=True
    )

    if not profile:
        return jsonify({'message': 'No profile found'}), 404

    return jsonify(profile)

@bp.route('', methods=['POST'])
def create_profile():
    """Create user profile"""
    data = request.json
    user_id = data.get('user_id', 1)

    # Calculate BMR and TDEE
    bmr = calculate_bmr(
        data['weight_kg'],
        data['height_cm'],
        data['age'],
        data['gender']
    )

    tdee = calculate_tdee(bmr, data['activity_level'])
    calorie_goal = calculate_calorie_goal(tdee, data['goal'])

    # Calculate macro targets based on calorie goal, weight, and goal
    macros = calculate_macro_targets(calorie_goal, data['weight_kg'], data['goal'])

    # Calculate water target
    water_target = calculate_water_target(data['weight_kg'], data['activity_level'])

    profile_id = execute_db(
        '''INSERT INTO user_profile
           (user_id, age, weight_kg, height_cm, gender, activity_level, goal, bmr, tdee,
            protein_target_g, carbs_target_g, fat_target_g, water_target_ml,
            use_custom_targets, custom_calorie_goal, custom_protein_target_g,
            custom_carbs_target_g, custom_fat_target_g, custom_water_target_ml)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        [
            user_id,
            data['age'],
            data['weight_kg'],
            data['height_cm'],
            data['gender'],
            data['activity_level'],
            data['goal'],
            bmr,
            tdee,
            macros['protein_g'],
            macros['carbs_g'],
            macros['fat_g'],
            water_target,
            data.get('use_custom_targets', False),
            data.get('custom_calorie_goal'),
            data.get('custom_protein_target_g'),
            data.get('custom_carbs_target_g'),
            data.get('custom_fat_target_g'),
            data.get('custom_water_target_ml')
        ]
    )

    # Populate vitamin targets with RDA values
    rdas = get_rda_targets(data['age'], data['gender'])
    for nutrient, amount in rdas.items():
        # Convert underscore names to display names
        nutrient_display = nutrient.replace('_', ' ').title()
        unit = 'mcg' if '_mcg' in nutrient else 'mg'

        # Insert or replace target
        execute_db(
            '''INSERT OR REPLACE INTO vitamin_targets
               (user_id, nutrient_name, target_amount, unit)
               VALUES (?, ?, ?, ?)''',
            [user_id, nutrient_display, amount, unit]
        )

    profile = query_db('SELECT * FROM user_profile WHERE id = ?', [profile_id], one=True)
    return jsonify(profile), 201

@bp.route('', methods=['PUT'])
def update_profile():
    """Update user profile"""
    data = request.json
    user_id = data.get('user_id', 1)

    # Get current profile to check if weight changed
    current_profile = query_db(
        'SELECT * FROM user_profile WHERE user_id = ?',
        [user_id],
        one=True
    )

    # Recalculate BMR, TDEE, and macro targets
    bmr = calculate_bmr(
        data['weight_kg'],
        data['height_cm'],
        data['age'],
        data['gender']
    )

    tdee = calculate_tdee(bmr, data['activity_level'])
    calorie_goal = calculate_calorie_goal(tdee, data['goal'])

    # Calculate macro targets based on calorie goal, weight, and goal
    macros = calculate_macro_targets(calorie_goal, data['weight_kg'], data['goal'])

    # Calculate water target
    water_target = calculate_water_target(data['weight_kg'], data['activity_level'])

    execute_db(
        '''UPDATE user_profile
           SET age = ?, weight_kg = ?, height_cm = ?, gender = ?,
               activity_level = ?, goal = ?, bmr = ?, tdee = ?,
               protein_target_g = ?, carbs_target_g = ?, fat_target_g = ?,
               water_target_ml = ?,
               use_custom_targets = ?,
               custom_calorie_goal = ?, custom_protein_target_g = ?,
               custom_carbs_target_g = ?, custom_fat_target_g = ?,
               custom_water_target_ml = ?,
               updated_at = CURRENT_TIMESTAMP
           WHERE user_id = ?''',
        [
            data['age'],
            data['weight_kg'],
            data['height_cm'],
            data['gender'],
            data['activity_level'],
            data['goal'],
            bmr,
            tdee,
            macros['protein_g'],
            macros['carbs_g'],
            macros['fat_g'],
            water_target,
            data.get('use_custom_targets', False),
            data.get('custom_calorie_goal'),
            data.get('custom_protein_target_g'),
            data.get('custom_carbs_target_g'),
            data.get('custom_fat_target_g'),
            data.get('custom_water_target_ml'),
            user_id
        ]
    )

    # Update today's daily log with new targets
    from datetime import date
    today = date.today().isoformat()
    execute_db(
        '''UPDATE daily_logs
           SET calorie_goal = ?,
               protein_target_g = ?,
               carbs_target_g = ?,
               fat_target_g = ?
           WHERE user_id = ? AND date = ?''',
        [calorie_goal, macros['protein_g'], macros['carbs_g'], macros['fat_g'], user_id, today]
    )

    # Auto-create weight log if weight changed
    new_weight = data['weight_kg']
    if current_profile and current_profile['weight_kg'] != new_weight:
        execute_db(
            '''INSERT OR REPLACE INTO weight_logs (user_id, date, weight_kg, notes)
               VALUES (?, ?, ?, ?)''',
            [user_id, today, new_weight, 'Updated from profile']
        )

    # Update vitamin targets if age or gender changed
    if not current_profile or current_profile['age'] != data['age'] or current_profile['gender'] != data['gender']:
        rdas = get_rda_targets(data['age'], data['gender'])
        for nutrient, amount in rdas.items():
            nutrient_display = nutrient.replace('_', ' ').title()
            unit = 'mcg' if '_mcg' in nutrient else 'mg'

            execute_db(
                '''INSERT OR REPLACE INTO vitamin_targets
                   (user_id, nutrient_name, target_amount, unit)
                   VALUES (?, ?, ?, ?)''',
                [user_id, nutrient_display, amount, unit]
            )

    profile = query_db('SELECT * FROM user_profile WHERE user_id = ?', [user_id], one=True)
    return jsonify(profile)

@bp.route('/update-day-targets/<date>', methods=['POST'])
def update_day_targets(date):
    """Update a specific day's targets from current profile"""
    user_id = request.args.get('user_id', 1)

    # Get current profile targets
    profile = query_db(
        'SELECT * FROM user_profile WHERE user_id = ?',
        [user_id],
        one=True
    )

    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    # Calculate calorie goal
    calorie_goal = calculate_calorie_goal(profile['tdee'], profile['goal'])

    # Update the daily log for this date
    execute_db(
        '''UPDATE daily_logs
           SET calorie_goal = ?,
               protein_target_g = ?,
               carbs_target_g = ?,
               fat_target_g = ?
           WHERE user_id = ? AND date = ?''',
        [
            calorie_goal,
            profile['protein_target_g'],
            profile['carbs_target_g'],
            profile['fat_target_g'],
            user_id,
            date
        ]
    )

    return jsonify({'message': 'Targets updated successfully', 'date': date})

@bp.route('/calculations', methods=['GET'])
def get_calculations():
    """Get BMR, TDEE, and calorie goal calculations"""
    user_id = request.args.get('user_id', 1)

    profile = query_db(
        'SELECT * FROM user_profile WHERE user_id = ?',
        [user_id],
        one=True
    )

    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    calorie_goal = calculate_calorie_goal(profile['tdee'], profile['goal'])

    return jsonify({
        'bmr': round(profile['bmr']),
        'tdee': round(profile['tdee']),
        'calorie_goal': round(calorie_goal),
        'goal': profile['goal'],
        'activity_level': profile['activity_level']
    })
