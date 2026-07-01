"""
Application initialization: sets up Flask app, Swagger documentation, routes and error handlers.
"""

import os
from flask import Flask
from app.api.handlers import register_error_handlers
from app.api.routers import register_routes
from flasgger import Swagger
import yaml

    

def create_app(config_object=None):
    from config import settings as default_settings
    config = config_object or default_settings

    app = Flask(__name__)
    app.config.from_object(config)
    
    with open(os.path.join(config.DOCS_DIR, 'swagger_template.yml'), 'r') as f:
        template = yaml.safe_load(f)


    swagger = Swagger(app, template=template)
    register_error_handlers(app)
    register_routes(app, config)

    return app

