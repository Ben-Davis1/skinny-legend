from flask import Blueprint, request, jsonify
from database import query_db, execute_db
from datetime import datetime

bp = Blueprint('weight_logs', __name__, url_prefix='/api/weight-logs')

@bp.route('', methods=['GET'])
def get_weight_logs():
    """Get all weight logs for a user"""
    user_id = request.args.get('user_id', 1)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date and end_date:
        logs = query_db(
            '''SELECT * FROM weight_logs
               WHERE user_id = ? AND date BETWEEN ? AND ?
               ORDER BY date ASC''',
            [user_id, start_date, end_date]
        )
    else:
        logs = query_db(
            'SELECT * FROM weight_logs WHERE user_id = ? ORDER BY date ASC',
            [user_id]
        )

    return jsonify(logs)

@bp.route('', methods=['POST'])
def create_weight_log():
    """Create or update a weight log entry"""
    data = request.json
    user_id = data.get('user_id', 1)
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    weight_kg = data['weight_kg']
    notes = data.get('notes', '')

    # Use INSERT OR REPLACE to handle updates
    execute_db(
        '''INSERT OR REPLACE INTO weight_logs (user_id, date, weight_kg, notes)
           VALUES (?, ?, ?, ?)''',
        [user_id, date, weight_kg, notes]
    )

    log = query_db(
        'SELECT * FROM weight_logs WHERE user_id = ? AND date = ?',
        [user_id, date],
        one=True
    )

    return jsonify(log), 201

@bp.route('/<int:log_id>', methods=['DELETE'])
def delete_weight_log(log_id):
    """Delete a weight log entry"""
    execute_db('DELETE FROM weight_logs WHERE id = ?', [log_id])
    return jsonify({'message': 'Weight log deleted'}), 200

@bp.route('/latest', methods=['GET'])
def get_latest_weight():
    """Get the most recent weight entry"""
    user_id = request.args.get('user_id', 1)

    log = query_db(
        '''SELECT * FROM weight_logs
           WHERE user_id = ?
           ORDER BY date DESC
           LIMIT 1''',
        [user_id],
        one=True
    )

    if not log:
        return jsonify({'message': 'No weight logs found'}), 404

    return jsonify(log)
