"""
routers.py

Contains FastAPI route(s) for file transcribing.
"""

from fastapi import APIRouter, Request
from app.core.schemas import SourceData
from app.core.transcriber import get_transcriber
from fastapi.responses import RedirectResponse


def register_router(app, settings):
    router = APIRouter()

    @router.post("/transcribe", responses=
                 {
                    400: {
                        "description": (
                            "Bad Request. "
                            "Codes: BAD_REQUEST."
                        )
                    },
                    404: {
                        "description": (
                            "Not Found. "
                            "Codes: FILE_NOT_FOUND_PATH."
                        )
                    },
                    422: {
                        "description": (
                            "Unprocessable Entity. "
                            "Codes: INVALID_FILE_PATH, TRANSCRIBER_NOT_IMPLEMENTED, FILE_MANAGER_NOT_IMPLEMENTED,"
                            " UNSUPPORTED_EXTENSION, SOURCE_IS_EMPTY_OR_INVALID."
                        )
                    },
                    500: {
                        "description": (
                            "Internal Server Error. "
                            "Codes: INTERNAL_ERROR."
                        )
                    }
                })
    def TranscribeFile(data: SourceData):

        """
        Transcribes a file from the provided source and saves it temporarily.

        - **file_path**: the path to transcribe
        - **file_name**: the file name to transcribe
        - **target_extension**: optional output extension
        - **language**: optional language

        """
        transcriber = get_transcriber(settings)
        response_data = transcriber.transcribe(data.file_path, 
                                               data.file_name, 
                                               data.target_extension, 
                                               data.language)
        return response_data
    

    @router.get("/")
    def redirect_to_docs(request: Request):
        """
        Redirects the root URL ("/") to the Swagger documentation at "/docs
        """
        return RedirectResponse(url="/docs")
    
    app.include_router(router)

