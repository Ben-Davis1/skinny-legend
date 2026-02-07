from flask import Blueprint, request, jsonify
from database import query_db, execute_db

bp = Blueprint('workouts', __name__, url_prefix='/api/workouts')

# Workout Sessions
@bp.route('/sessions', methods=['POST'])
def create_session():
    """Create a new workout session"""
    data = request.json

    session_id = execute_db(
        '''INSERT INTO workout_sessions (daily_log_id, name, notes)
           VALUES (?, ?, ?)''',
        [data['daily_log_id'], data.get('name'), data.get('notes', '')]
    )

    session = query_db('SELECT * FROM workout_sessions WHERE id = ?', [session_id], one=True)
    return jsonify(session), 201

@bp.route('/sessions/<int:daily_log_id>', methods=['GET'])
def get_sessions(daily_log_id):
    """Get all workout sessions for a daily log"""
    sessions = query_db(
        '''SELECT * FROM workout_sessions
           WHERE daily_log_id = ?
           ORDER BY started_at DESC''',
        [daily_log_id]
    )
    return jsonify(sessions)

@bp.route('/sessions/<int:session_id>', methods=['PUT'])
def update_session(session_id):
    """Update workout session (mark completed, add notes)"""
    data = request.json

    execute_db(
        '''UPDATE workout_sessions
           SET name = ?, notes = ?, completed_at = ?
           WHERE id = ?''',
        [data.get('name'), data.get('notes'), data.get('completed_at'), session_id]
    )

    session = query_db('SELECT * FROM workout_sessions WHERE id = ?', [session_id], one=True)
    return jsonify(session)

@bp.route('/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a workout session (cascades to exercises and sets)"""
    execute_db('DELETE FROM workout_sessions WHERE id = ?', [session_id])
    return jsonify({'message': 'Session deleted successfully'}), 200

# Workout Exercises
@bp.route('/exercises', methods=['POST'])
def create_exercise():
    """Add an exercise to a workout session"""
    data = request.json

    exercise_id = execute_db(
        '''INSERT INTO workout_exercises
           (workout_session_id, exercise_name, exercise_category, order_index, notes)
           VALUES (?, ?, ?, ?, ?)''',
        [
            data['workout_session_id'],
            data['exercise_name'],
            data.get('exercise_category', ''),
            data.get('order_index', 0),
            data.get('notes', '')
        ]
    )

    exercise = query_db('SELECT * FROM workout_exercises WHERE id = ?', [exercise_id], one=True)
    return jsonify(exercise), 201

@bp.route('/exercises/<int:session_id>', methods=['GET'])
def get_exercises(session_id):
    """Get all exercises for a workout session"""
    exercises = query_db(
        '''SELECT * FROM workout_exercises
           WHERE workout_session_id = ?
           ORDER BY order_index, created_at''',
        [session_id]
    )
    return jsonify(exercises)

@bp.route('/exercises/<int:exercise_id>', methods=['DELETE'])
def delete_exercise(exercise_id):
    """Delete an exercise (cascades to sets)"""
    execute_db('DELETE FROM workout_exercises WHERE id = ?', [exercise_id])
    return jsonify({'message': 'Exercise deleted successfully'}), 200

# Workout Sets
@bp.route('/sets', methods=['POST'])
def create_set():
    """Log a set for an exercise"""
    data = request.json

    set_id = execute_db(
        '''INSERT INTO workout_sets
           (workout_exercise_id, set_number, reps, weight_kg, rpe, completed, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        [
            data['workout_exercise_id'],
            data['set_number'],
            data['reps'],
            data.get('weight_kg'),
            data.get('rpe'),
            data.get('completed', True),
            data.get('notes', '')
        ]
    )

    set_data = query_db('SELECT * FROM workout_sets WHERE id = ?', [set_id], one=True)
    return jsonify(set_data), 201

@bp.route('/sets/<int:exercise_id>', methods=['GET'])
def get_sets(exercise_id):
    """Get all sets for an exercise"""
    sets = query_db(
        '''SELECT * FROM workout_sets
           WHERE workout_exercise_id = ?
           ORDER BY set_number''',
        [exercise_id]
    )
    return jsonify(sets)

@bp.route('/sets/<int:set_id>', methods=['PUT'])
def update_set(set_id):
    """Update a set (edit reps/weight/completion)"""
    data = request.json

    execute_db(
        '''UPDATE workout_sets
           SET reps = ?, weight_kg = ?, rpe = ?, completed = ?, notes = ?
           WHERE id = ?''',
        [
            data['reps'],
            data.get('weight_kg'),
            data.get('rpe'),
            data.get('completed', True),
            data.get('notes', ''),
            set_id
        ]
    )

    set_data = query_db('SELECT * FROM workout_sets WHERE id = ?', [set_id], one=True)
    return jsonify(set_data)

@bp.route('/sets/<int:set_id>', methods=['DELETE'])
def delete_set(set_id):
    """Delete a set"""
    execute_db('DELETE FROM workout_sets WHERE id = ?', [set_id])
    return jsonify({'message': 'Set deleted successfully'}), 200

# History & Analytics
@bp.route('/history/<exercise_name>', methods=['GET'])
def get_exercise_history(exercise_name):
    """Get historical data for a specific exercise"""
    user_id = request.args.get('user_id', 1)
    limit = int(request.args.get('limit', 10))

    history = query_db(
        '''SELECT
               we.exercise_name,
               we.created_at,
               ws.set_number,
               ws.reps,
               ws.weight_kg,
               ws.rpe,
               dl.date
           FROM workout_sets ws
           JOIN workout_exercises we ON ws.workout_exercise_id = we.id
           JOIN workout_sessions wses ON we.workout_session_id = wses.id
           JOIN daily_logs dl ON wses.daily_log_id = dl.id
           WHERE LOWER(we.exercise_name) = LOWER(?) AND dl.user_id = ?
           ORDER BY we.created_at DESC
           LIMIT ?''',
        [exercise_name, user_id, limit * 10]
    )

    return jsonify(history)

@bp.route('/stats/<exercise_name>', methods=['GET'])
def get_exercise_stats(exercise_name):
    """Get PRs and stats for an exercise"""
    user_id = request.args.get('user_id', 1)

    stats = query_db(
        '''SELECT
               MAX(ws.weight_kg) as max_weight,
               MAX(ws.reps) as max_reps,
               MAX(ws.weight_kg * ws.reps) as max_volume,
               COUNT(DISTINCT we.id) as total_sessions,
               SUM(ws.reps * ws.weight_kg) as total_volume
           FROM workout_sets ws
           JOIN workout_exercises we ON ws.workout_exercise_id = we.id
           JOIN workout_sessions wses ON we.workout_session_id = wses.id
           JOIN daily_logs dl ON wses.daily_log_id = dl.id
           WHERE LOWER(we.exercise_name) = LOWER(?) AND dl.user_id = ?''',
        [exercise_name, user_id],
        one=True
    )

    return jsonify(stats)

@bp.route('/recent-exercises', methods=['GET'])
def get_recent_exercises():
    """Get recently used unique exercises"""
    user_id = request.args.get('user_id', 1)
    limit = int(request.args.get('limit', 15))

    exercises = query_db(
        '''SELECT
               exercise_name,
               exercise_category,
               MAX(created_at) as last_used
           FROM workout_exercises we
           JOIN workout_sessions ws ON we.workout_session_id = ws.id
           JOIN daily_logs dl ON ws.daily_log_id = dl.id
           WHERE dl.user_id = ?
           GROUP BY LOWER(exercise_name)
           ORDER BY last_used DESC
           LIMIT ?''',
        [user_id, limit]
    )

    return jsonify(exercises)

@bp.route('/session-details/<int:session_id>', methods=['GET'])
def get_session_details(session_id):
    """Get complete session with all exercises and sets"""
    session = query_db('SELECT * FROM workout_sessions WHERE id = ?', [session_id], one=True)

    if not session:
        return jsonify({'error': 'Session not found'}), 404

    exercises = query_db(
        '''SELECT * FROM workout_exercises
           WHERE workout_session_id = ?
           ORDER BY order_index, created_at''',
        [session_id]
    )

    # Get sets for each exercise
    for exercise in exercises:
        exercise['sets'] = query_db(
            '''SELECT * FROM workout_sets
               WHERE workout_exercise_id = ?
               ORDER BY set_number''',
            [exercise['id']]
        )

    session['exercises'] = exercises
    return jsonify(session)

@bp.route('/daily-summary', methods=['GET'])
def get_daily_summary():
    """Get workout summary for date range (for history page)"""
    user_id = request.args.get('user_id', 1)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date required'}), 400

    summaries = query_db(
        '''SELECT
               dl.date,
               COUNT(DISTINCT ws.id) as workout_count,
               COUNT(DISTINCT we.id) as total_exercises,
               COUNT(ws_sets.id) as total_sets,
               COALESCE(SUM(ws_sets.reps * ws_sets.weight_kg), 0) as total_volume,
               GROUP_CONCAT(DISTINCT COALESCE(ws.name, 'Workout')) as workout_names
           FROM daily_logs dl
           LEFT JOIN workout_sessions ws ON dl.id = ws.daily_log_id
           LEFT JOIN workout_exercises we ON ws.id = we.workout_session_id
           LEFT JOIN workout_sets ws_sets ON we.id = ws_sets.workout_exercise_id
           WHERE dl.user_id = ? AND dl.date BETWEEN ? AND ?
           GROUP BY dl.date
           HAVING workout_count > 0
           ORDER BY dl.date''',
        [user_id, start_date, end_date]
    )

    return jsonify(summaries)

@bp.route('/by-date/<date>', methods=['GET'])
def get_workouts_by_date(date):
    """Get all workouts for a specific date with full details"""
    user_id = request.args.get('user_id', 1)

    # Get daily log for this date
    daily_log = query_db(
        'SELECT id FROM daily_logs WHERE date = ? AND user_id = ?',
        [date, user_id],
        one=True
    )

    if not daily_log:
        return jsonify([])

    # Get all sessions for this date
    sessions = query_db(
        '''SELECT * FROM workout_sessions
           WHERE daily_log_id = ?
           ORDER BY started_at DESC''',
        [daily_log['id']]
    )

    # Get full details for each session
    for session in sessions:
        exercises = query_db(
            '''SELECT * FROM workout_exercises
               WHERE workout_session_id = ?
               ORDER BY order_index, created_at''',
            [session['id']]
        )

        for exercise in exercises:
            exercise['sets'] = query_db(
                '''SELECT * FROM workout_sets
                   WHERE workout_exercise_id = ?
                   ORDER BY set_number''',
                [exercise['id']]
            )

        session['exercises'] = exercises

    return jsonify(sessions)
