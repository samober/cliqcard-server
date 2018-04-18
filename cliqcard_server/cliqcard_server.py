import os
from .app import create_app


config_name = os.getenv('CLIQCARD_SERVER_MODE', 'development')
app = create_app(config_name)