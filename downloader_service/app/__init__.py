"""
Application initialization: sets up FastAPI app,  routes and error handlers.
"""

from fastapi import FastAPI
from app.api.handlers import register_error_handlers
from app.api.routers import register_router
from config import settings as default_settings
    

def create_app(config_object=None):
    """
    Creates and configures a FastAPI app instance with routes and error handlers.
    """
    config = config_object or default_settings

    app = FastAPI()
    register_error_handlers(app)
    register_router(app, config)

    return app

