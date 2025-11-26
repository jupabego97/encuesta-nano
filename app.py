"""
NANOTRONICS SURVEY - Backend Flask
Simple backend to save survey responses to a PostgreSQL database.
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import os
import click

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql://user:password@localhost/survey_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class SurveyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.JSON)

    def to_dict(self):
        return {
            'id': self.id,
            'submission_timestamp': self.submission_timestamp.isoformat(),
            'data': self.data
        }

# --- Command to initialize the database ---
@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables."""
    db.create_all()
    click.echo("Initialized the database.")

# --- Routes ---
@app.route('/')
def index():
    """Serve the main survey page"""
    return render_template('index.html')

@app.route('/api/submit', methods=['POST'])
def submit_survey():
    """Handle survey submission and save to database"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400

        # Add server timestamp to the data blob
        data['server_timestamp'] = datetime.utcnow().isoformat()
        
        # Create a new response record
        new_response = SurveyResponse(data=data)
        
        # Add to session and commit
        db.session.add(new_response)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '¡Respuesta guardada correctamente!',
            'id': new_response.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f'Error saving response: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/responses', methods=['GET'])
def get_responses():
    """Get all responses from the database"""
    try:
        responses = SurveyResponse.query.order_by(SurveyResponse.submission_timestamp.desc()).all()
        response_list = [r.to_dict() for r in responses]
        
        return jsonify({
            'total': len(response_list),
            'responses': response_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get basic survey statistics from the database"""
    try:
        total_responses = db.session.query(func.count(SurveyResponse.id)).scalar()

        if total_responses == 0:
            return jsonify({'total_responses': 0, 'message': 'No hay respuestas aún'}), 200

        # Helper to extract and count JSON property
        def get_json_property_distribution(prop):
            results = db.session.query(SurveyResponse.data[prop].astext, func.count(SurveyResponse.id)).group_by(SurveyResponse.data[prop].astext).all()
            return {key: value for key, value in results if key}

        # Helper to calculate average of a JSON property
        def get_json_property_average(prop):
            avg = db.session.query(func.avg(func.cast(SurveyResponse.data[prop], db.Float))).scalar()
            return round(avg, 2) if avg is not None else None

        stats = {
            'total_responses': total_responses,
            'q1_distribution': get_json_property_distribution('q1'),
            'q3_distribution': get_json_property_distribution('q3'),
            'q6_average': get_json_property_average('q6'),
            'q7_average': get_json_property_average('q7_slider'),
            'q10_average': get_json_property_average('q10_trust'),
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"Error calculating stats: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print('🚀 Nanotronics Survey Server')
    print(f'📊 Abre http://localhost:{port} en tu navegador')
    print('-' * 40)
    app.run(debug=debug, host='0.0.0.0', port=port)
