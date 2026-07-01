"""
Application initialization: sets up Flask app, routes and error handlers.
"""


from flask import Flask
from app.routers import register_routes
from app.handlers import register_error_handlers

    

def create_app(config_object=None):
    from config import settings as default_settings
    config = config_object or default_settings

    app = Flask(
        __name__,
        template_folder="../templates"
    )

    register_routes(app, config)
    register_error_handlers(app)

    return app

    

