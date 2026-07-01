"""
Application initialization: sets up FastAPI app,  routes and error handlers.
"""

from fastapi import FastAPI, Request


    

def create_app(config_object=None):
    """
    Creates and configures a FastAPI app instance with routes and error handlers.
    """
    from app.api.handlers import register_error_handlers
    from app.api.routers import register_router
    from config import settings as default_settings
    config = config_object or default_settings

    app = FastAPI()

    @app.middleware("http")
    async def save_request_data(request: Request, call_next):
        """
        is used for saving request data, so it will be saved to the log
        """
        content_type = request.headers.get("content-type", "")

        if "application/json" in content_type:
            body = await request.body()
            request.state.json_body = body

        response = await call_next(request)
        return response
    
    register_error_handlers(app)
    register_router(app, config)

    return app

