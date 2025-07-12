import os
from .config import Config, DevelopmentConfig, ProductionConfig, TestingConfig

def get_config():
    """Get configuration based on environment."""
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return configs.get(config_name, DevelopmentConfig)

__all__ = ['Config', 'DevelopmentConfig', 'ProductionConfig', 'TestingConfig', 'get_config'] 