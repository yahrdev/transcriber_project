"""
routers.py

Contains FastAPI route(s) for file downloading.
"""

from fastapi import APIRouter, Request
from app.core.schemas import SourceData
from app.core.extractor import get_extractor
from fastapi.responses import RedirectResponse


def register_router(app, settings):
    router = APIRouter()

    @router.post("/download", responses=
                 {
                    400: {
                        "description": (
                            "Bad Request. "
                            "Codes: WRONG_TYPE."
                        )
                    },
                    404: {
                        "description": (
                            "Not Found. "
                            "Codes: FILE_NOT_FOUND_PATH, URL_UNREACHABLE."
                        )
                    },
                    422: {
                        "description": (
                            "Unprocessable Entity. "
                            "Codes: WRONG_EXTRACTOR, WRONG_SOURCE_TYPE, INVALID_FILE_PATH, "
                            "EXTENSION_MISMATCH, UNSUPPORTED_EXTENSION, NOT_URL, SOURCE_IS_EMPTY_OR_INVALID."
                        )
                    },
                    500: {
                        "description": (
                            "Internal Server Error. "
                            "Codes: FILE_MANAGER_NOT_IMPLEMENTED, INTERNAL_ERROR."
                        )
                    }
                })
    def Download_File(data: SourceData):

        """
        Downloads a file from the provided source and saves it temporarily.

        - **source_type**: can be "url" or "path"
        - **source**: the remote URL or local path to download
        - **auth**: optional authorization data
        """
        extractor = get_extractor(data.source_type, settings)
        response_data = extractor.extract(data.auth, data.source)
        return response_data
    

    @router.get("/")
    def redirect_to_docs(request: Request):
        """
        Redirects the root URL ("/") to the Swagger documentation at "/docs
        """
        return RedirectResponse(url="/docs")
    
    app.include_router(router)

