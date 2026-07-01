"""
main.py

Entry point for running the FastAPI application.

"""
from config import settings
from app import create_app

app = create_app(settings)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)


# uvicorn app.main:app --reload --port 8001

