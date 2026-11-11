"""
routers.py

Contains FastAPI route(s) for file transcription.
"""

from fastapi import APIRouter, Request, FastAPI, File, Form, UploadFile
from app.models.api_schemas import SourceData, ResponseStatusModel
from fastapi.responses import RedirectResponse
from typing import Annotated
from fastapi.responses import FileResponse
import app.services.job_service as job_service
from app.services.job_pipeline import JobPipeline


def register_router(app, settings):
    router = APIRouter()
    job_pipeline = JobPipeline(settings=settings)

    @router.post("/jobs", status_code=202, responses={
        400: {
            "description": (
                "Bad Request. "
                "Codes: BAD_REQUEST."
            )
        },
        422: {
            "description": (
                "Unprocessable Entity. "
                "Codes: SOURCE_IS_EMPTY_OR_INVALID, "
                "FILE_CORRUPTED, INVALID_LANGUAGE_FORMAT."
            )
        },
        500: {
            "description": "Internal Server Error."
        },
    })
    def create_job(data: SourceData):

        """
        Creates a transcription job from an external media source.

        - **client_id**: identifier of the client who submits the job
        - **source_type**: source type, for example "reference"
        - **source**: media source reference, URL, or file path available to the service
        - **language**: transcription language in ISO-639-1 format, for example "uk" or "en"

        The job is created with status "pending" and put into the Celery queue.
        The response (202) contains only job_id, the processing runs in the background:
        the worker downloads the source, converts it to audio and transcribes it.

        Use /jobs/{job_id}/status to check the progress
        and /jobs/{job_id}/result/download to get the result.
        """
        
        return job_pipeline.start_reference(data)
    
    
    @router.post("/jobs/upload", status_code=202, responses={
        400: {
            "description": (
                "Bad Request. "
                "Codes: BAD_REQUEST."
            )
        },
        422: {
            "description": (
                "Unprocessable Entity. "
                "Codes: UNKNOWN_TYPE, FILE_CORRUPTED, INVALID_LANGUAGE_FORMAT, INVALID_FILE_EXTENSION"
            )
        },
        500: {
            "description": "Internal Server Error."
        },
        })
    def create_job_file(
                        request: Request,
                        client_id:Annotated[str, Form()],
                        language: Annotated[str, Form()],
                        file: Annotated[UploadFile, File()]
                        ):

        """
        Creates a transcription job from an uploaded media file.

        - **client_id**: identifier of the client who submits the job
        - **language**: transcription language in ISO-639-1 format, for example "uk" or "en"
        - **file**: uploaded audio or video file

        The uploaded file is validated and saved to the shared storage,
        then the job is put into the Celery queue.
        The response (202) contains only job_id, the worker converts
        and transcribes the file in the background.

        Files bigger than MAX_UPLOAD_MB are rejected with 413 (BIG_FILE).
        """

        request.state.form_data = {
            "client_id": client_id,
            "language": language,
            "filename": file.filename,
            "content_type": file.content_type,
                                }
        
        return job_pipeline.start_upload(client_id=client_id, 
                                          language=language,
                                          file=file)
    
    
    @router.get("/jobs/{job_id}/result/download", responses={
        400: {
            "description": (
                "Bad Request. "
                "Codes: BAD_REQUEST."
            )
        },
        500: {
            "description": "Internal Server Error."
        },
    })
    def get_result(request: Request, job_id: str):
        """
        Downloads the transcription result for an existing job.

        - **job_id**: identifier of the transcription job

        Returns the generated text file if the job is completed.
        If the job is still in progress (NOT_FINISHED) or failed (JOB_FAILED), returns 409.
        """
        request.state.params = {
                                "job_id": job_id
                                }
        js = job_service.JobService(settings=settings)
        file_path, file_name = js.get_file_path_name_by_job_id(job_id=job_id)

        return FileResponse(
            path=file_path,
            filename=f"{file_name}.txt" if not file_name.endswith(".txt") else file_name,   
            media_type="text/plain" 
        )

    @router.get("/jobs/{job_id}/status", responses={
        400: {
            "description": (
                "Bad Request. "
                "Codes: BAD_REQUEST."
            )
        },
        500: {
            "description": "Internal Server Error."
        },
    })
    def get_status(request: Request, job_id: str):
        """
        Get status of the transcription job.

        - **job_id**: identifier of the transcription job

        Status values: pending, processing, completed, failed.
        Clients call this endpoint repeatedly (polling) until the job is finished.
        """
        request.state.params = {
                                "job_id": job_id
                                }
        js = job_service.JobService(settings=settings)
        status = js.get_job_status(job_id=job_id)

        return ResponseStatusModel(job_id=job_id,
                                   status = status)
    

    @router.get("/")
    def redirect_to_docs(request: Request):
        """
        Redirects the root URL ("/") to the Swagger documentation at "/docs
        """
        
        return RedirectResponse(url="/docs")
    
    app.include_router(router)