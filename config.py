"""
NANOTRONICS SURVEY - Configuration Module
Centralized configuration with environment variable support
"""

import os
from typing import List


class Config:
    """Base configuration class"""
    
    # Flask
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Server
    PORT: int = int(os.environ.get('PORT', 5000))
    HOST: str = os.environ.get('HOST', '0.0.0.0')
    
    # Environment
    FLASK_ENV: str = os.environ.get('FLASK_ENV', 'production')
    DEBUG: bool = FLASK_ENV != 'production'
    
    # Database
    # Railway provides DATABASE_URL automatically when you add PostgreSQL
    DATABASE_URL: str = os.environ.get('DATABASE_URL', '')
    
    # Handle Railway's postgres:// vs postgresql:// URL format
    @classmethod
    def get_database_url(cls) -> str:
        """Get properly formatted database URL"""
        url = cls.DATABASE_URL
        # SQLAlchemy requires postgresql:// instead of postgres://
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        return url
    
    SQLALCHEMY_DATABASE_URI: str = property(lambda self: self.get_database_url())
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 5,
        'max_overflow': 10,
    }
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.environ.get(
        'ALLOWED_ORIGINS', 
        '*'
    ).split(',')
    
    # Logging
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT: str = os.environ.get('LOG_FORMAT', 'json')  # json or text
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_REQUESTS: int = int(os.environ.get('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_WINDOW: int = int(os.environ.get('RATE_LIMIT_WINDOW', 60))  # seconds
    
    # Storage (fallback for file-based storage)
    RESPONSES_DIR: str = os.environ.get('RESPONSES_DIR', 'responses')
    
    # Application Info
    APP_NAME: str = 'Nanotronics Survey'
    APP_VERSION: str = '1.1.0'
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.FLASK_ENV == 'production'
    
    @classmethod
    def has_database(cls) -> bool:
        """Check if database is configured"""
        return bool(cls.DATABASE_URL)
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate configuration and return list of warnings"""
        warnings = []
        
        if cls.is_production():
            if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
                warnings.append('SECRET_KEY is using default value in production!')
            
            if '*' in cls.ALLOWED_ORIGINS:
                warnings.append('CORS is allowing all origins in production!')
            
            if not cls.has_database():
                warnings.append('DATABASE_URL not set - using file-based storage (data will be lost on restart)')
        
        return warnings
    
    @classmethod
    def to_dict(cls) -> dict:
        """Return configuration as dictionary (excluding sensitive values)"""
        return {
            'app_name': cls.APP_NAME,
            'app_version': cls.APP_VERSION,
            'environment': cls.FLASK_ENV,
            'debug': cls.DEBUG,
            'log_level': cls.LOG_LEVEL,
            'rate_limit_enabled': cls.RATE_LIMIT_ENABLED,
            'database_configured': cls.has_database(),
        }


class DevelopmentConfig(Config):
    """Development configuration"""
    FLASK_ENV = 'development'
    DEBUG = True
    LOG_FORMAT = 'text'


class ProductionConfig(Config):
    """Production configuration"""
    FLASK_ENV = 'production'
    DEBUG = False
    LOG_FORMAT = 'json'


class TestingConfig(Config):
    """Testing configuration"""
    FLASK_ENV = 'testing'
    DEBUG = True
    TESTING = True


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'production')
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    
    return configs.get(env, ProductionConfig)
