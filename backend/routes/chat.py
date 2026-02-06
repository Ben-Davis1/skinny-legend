from flask import Blueprint, request, jsonify, stream_with_context, Response
from services.ai_service import get_food_suggestions
import json

bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@bp.route('', methods=['POST'])
def chat():
    """Chat with AI to add food entries"""
    data = request.json
    message = data.get('message')
    conversation_history = data.get('history', [])
    context = data.get('context', {})

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        result = get_food_suggestions(message, conversation_history, context)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/stream', methods=['POST'])
def chat_stream():
    """Stream chat responses (for future implementation)"""
    # This can be implemented later for real-time streaming
    return jsonify({'error': 'Streaming not yet implemented'}), 501
