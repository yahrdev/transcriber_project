
"""
main.py

Entry point for running the Flask application.

"""

from config import settings
from app import create_app

app = create_app(settings)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.PORT, debug=settings.DEBUG_PROGRESS)

    #http://127.0.0.1:7999/apidocs/

    #flask run --port 7999

