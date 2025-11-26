"""
NANOTRONICS SURVEY - Backend Flask
Simple backend to save survey responses
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Directory to store responses
RESPONSES_DIR = 'responses'

# Ensure responses directory exists
if not os.path.exists(RESPONSES_DIR):
    os.makedirs(RESPONSES_DIR)


@app.route('/')
def index():
    """Serve the main survey page"""
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS)"""
    return send_from_directory('.', path)


@app.route('/api/submit', methods=['POST'])
def submit_survey():
    """Handle survey submission"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Add server timestamp
        data['server_timestamp'] = datetime.now().isoformat()
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'response_{timestamp}.json'
        filepath = os.path.join(RESPONSES_DIR, filename)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Also append to a master CSV for easy viewing
        append_to_csv(data)
        
        return jsonify({
            'success': True,
            'message': '¡Respuesta guardada correctamente!',
            'id': timestamp
        }), 200
        
    except Exception as e:
        print(f'Error saving response: {e}')
        return jsonify({'error': str(e)}), 500


def append_to_csv(data):
    """Append response to master CSV file"""
    import csv
    
    csv_file = os.path.join(RESPONSES_DIR, 'all_responses.csv')
    file_exists = os.path.exists(csv_file)
    
    # Flatten nested data
    flat_data = {}
    for key, value in data.items():
        if isinstance(value, list):
            flat_data[key] = ', '.join(str(v) for v in value)
        else:
            flat_data[key] = str(value)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=flat_data.keys())
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(flat_data)


@app.route('/api/responses', methods=['GET'])
def get_responses():
    """Get all responses (for admin view)"""
    try:
        responses = []
        
        for filename in os.listdir(RESPONSES_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(RESPONSES_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    responses.append(json.load(f))
        
        # Sort by timestamp (newest first)
        responses.sort(key=lambda x: x.get('server_timestamp', ''), reverse=True)
        
        return jsonify({
            'total': len(responses),
            'responses': responses
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get basic survey statistics"""
    try:
        responses = []
        
        for filename in os.listdir(RESPONSES_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(RESPONSES_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    responses.append(json.load(f))
        
        if not responses:
            return jsonify({
                'total_responses': 0,
                'message': 'No hay respuestas aún'
            }), 200
        
        # Calculate basic stats
        stats = {
            'total_responses': len(responses),
            'q1_distribution': count_values(responses, 'q1'),
            'q3_distribution': count_values(responses, 'q3'),
            'q6_average': calculate_average(responses, 'q6'),
            'q7_average': calculate_average(responses, 'q7_slider'),
            'q10_average': calculate_average(responses, 'q10_trust'),
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def count_values(responses, key):
    """Count occurrences of each value for a key"""
    counts = {}
    for response in responses:
        value = response.get(key)
        if value:
            counts[value] = counts.get(value, 0) + 1
    return counts


def calculate_average(responses, key):
    """Calculate average for numeric values"""
    values = []
    for response in responses:
        value = response.get(key)
        if value:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    
    if values:
        return round(sum(values) / len(values), 2)
    return None


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print('🚀 Nanotronics Survey Server')
    print(f'📊 Abre http://localhost:{port} en tu navegador')
    print('-' * 40)
    app.run(debug=debug, host='0.0.0.0', port=port)

