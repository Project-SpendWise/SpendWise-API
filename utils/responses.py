from flask import jsonify
from datetime import datetime

def success_response(data=None, message=None, status_code=200):
    """Create a standardized success response"""
    response = {
        'success': True,
        'data': data,
        'metadata': {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0'
        }
    }
    if message:
        response['message'] = message
    return jsonify(response), status_code

def error_response(message, error_code='ERROR', status_code=400, details=None):
    """Create a standardized error response"""
    response = {
        'success': False,
        'error': {
            'message': message,
            'code': error_code,
            'statusCode': status_code
        }
    }
    if details:
        response['error']['details'] = details
    return jsonify(response)

