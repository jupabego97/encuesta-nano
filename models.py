"""
NANOTRONICS SURVEY - Database Models
SQLAlchemy models for PostgreSQL
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class SurveyResponse(db.Model):
    """Model for storing survey responses"""
    
    __tablename__ = 'survey_responses'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    client_timestamp = db.Column(db.String(50), nullable=True)
    
    # Client info
    client_ip = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    
    # Question 1: ¿Hace cuánto conoces Nanotronics?
    q1_time_known = db.Column(db.String(50), nullable=True)
    
    # Question 2: ¿Qué es lo primero que piensas?
    q2_first_thought = db.Column(db.Text, nullable=True)
    q2_tags = db.Column(db.Text, nullable=True)  # JSON array as string
    
    # Question 3: Experiencia comprando
    q3_experience = db.Column(db.String(50), nullable=True)
    
    # Question 4: ¿Qué te gusta más?
    q4_likes = db.Column(db.Text, nullable=True)  # JSON array as string
    q4_why = db.Column(db.Text, nullable=True)
    
    # Question 5: ¿Qué podríamos mejorar?
    q5_improvements = db.Column(db.Text, nullable=True)  # JSON array as string
    q5_comment = db.Column(db.Text, nullable=True)
    
    # Question 6: Atención del personal (1-5)
    q6_staff_rating = db.Column(db.Integer, nullable=True)
    
    # Question 7: Productos actualizados (1-5)
    q7_products_updated = db.Column(db.Integer, nullable=True)
    q7_comment = db.Column(db.Text, nullable=True)
    
    # Question 8: Productos deseados
    q8_desired_products = db.Column(db.Text, nullable=True)  # JSON array as string
    q8_other = db.Column(db.Text, nullable=True)
    
    # Question 9: Personalidad de la marca
    q9_brand_personality = db.Column(db.Text, nullable=True)
    q9_tags = db.Column(db.Text, nullable=True)
    
    # Question 10: Confianza (1-5)
    q10_trust = db.Column(db.Integer, nullable=True)
    q10_comment = db.Column(db.Text, nullable=True)
    
    # Question 11: ¿Qué comunicar más?
    q11_communicate = db.Column(db.Text, nullable=True)  # JSON array as string
    q11_other = db.Column(db.Text, nullable=True)
    
    # Raw JSON data (backup)
    raw_data = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<SurveyResponse {self.id} - {self.created_at}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'client_timestamp': self.client_timestamp,
            'client_ip': self.client_ip,
            'user_agent': self.user_agent,
            'q1': self.q1_time_known,
            'q2': self.q2_first_thought,
            'q2_tags': self.q2_tags,
            'q3': self.q3_experience,
            'q4': self.q4_likes,
            'q4_why': self.q4_why,
            'q5': self.q5_improvements,
            'q5_comment': self.q5_comment,
            'q6': self.q6_staff_rating,
            'q7_slider': self.q7_products_updated,
            'q7': self.q7_comment,
            'q8_tags': self.q8_desired_products,
            'q8': self.q8_other,
            'q9': self.q9_brand_personality,
            'q9_tags': self.q9_tags,
            'q10_trust': self.q10_trust,
            'q10': self.q10_comment,
            'q11': self.q11_communicate,
            'q11_other': self.q11_other,
        }
    
    @classmethod
    def from_survey_data(cls, data: dict):
        """Create model instance from survey submission data"""
        import json
        
        def to_json_string(value):
            """Convert list or value to JSON string"""
            if isinstance(value, list):
                return json.dumps(value)
            return value
        
        def to_int(value):
            """Safely convert to integer"""
            if value is None:
                return None
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        
        return cls(
            client_timestamp=data.get('timestamp'),
            client_ip=data.get('client_ip'),
            user_agent=data.get('user_agent'),
            q1_time_known=data.get('q1'),
            q2_first_thought=data.get('q2'),
            q2_tags=to_json_string(data.get('q2_tags')),
            q3_experience=data.get('q3'),
            q4_likes=to_json_string(data.get('q4')),
            q4_why=data.get('q4_why'),
            q5_improvements=to_json_string(data.get('q5')),
            q5_comment=data.get('q5_comment'),
            q6_staff_rating=to_int(data.get('q6')),
            q7_products_updated=to_int(data.get('q7_slider')),
            q7_comment=data.get('q7'),
            q8_desired_products=to_json_string(data.get('q8_tags')),
            q8_other=data.get('q8'),
            q9_brand_personality=data.get('q9'),
            q9_tags=to_json_string(data.get('q9_tags')),
            q10_trust=to_int(data.get('q10_trust')),
            q10_comment=data.get('q10'),
            q11_communicate=to_json_string(data.get('q11')),
            q11_other=data.get('q11_other'),
            raw_data=json.dumps(data, ensure_ascii=False),
        )

