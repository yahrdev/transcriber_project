"""
tasks.py

Celery tasks executed by the worker.

The gateway only puts these tasks into the Redis queue (.delay()),
the celery_worker container takes them from the queue and runs the processing.
All arguments are plain strings because Celery sends them to the worker as JSON.
"""

from app.services.job_pipeline import JobPipeline
from app.celery_app import celery_app
from config import settings


@celery_app.task
def transcribe_upload_job(job_id: str, language: str, tmp_path: str, file_name: str, file_extension: str):

    """
    Processes a job created from an uploaded file.

    The file is already saved to the shared folder by the gateway,
    so the worker only converts and transcribes it.
    """

    job_pipeline = JobPipeline(settings)  # created inside the task, so each worker process has its own Mongo connection
    job_pipeline.run_upload(job_id = job_id,
               language = language,
               tmp_path = tmp_path,
               file_name = file_name,
               file_extension = file_extension)


@celery_app.task
def transcribe_reference_job(job_id: str, source_type: str, source: str, language: str):

    """
    Processes a job created from an external source (URL or file path).

    The worker downloads the media, converts and transcribes it.
    """

    job_pipeline = JobPipeline(settings)  # created inside the task, so each worker process has its own Mongo connection
    job_pipeline.run_reference(job_id = job_id,
                  source_type = source_type,
                  source = source,
                  language = language)
