"""
Orchestrates the transcription processing pipeline.
"""


import app.services.job_service as job_service
import app.microservices.microservice_clients as M
from app.models.job_schemas import JobStatus, JobSourceType
import uuid
from app.services.media_validation import validate_media_file, validate_media_mime, validate_language
from app.api.handlers import build_job_error
import app.models.api_schemas as api_models
from app.services.file_manager import get_file_manager
from app.exceptions.exceptions import AppError
from app.utils.extensions import extract_extension

class JobPipeline:

    """
    Runs a transcription job in two parts.

    start_* methods run in the gateway: validate the request, create the job (pending),
    put a Celery task into the queue and return job_id immediately.

    run_* methods run in the celery_worker: download/convert/transcribe the media
    and update the job status (processing -> completed or failed).
    """

    def __init__(self, settings):
        self.downloader = M.DownloaderClient(settings=settings)
        self.converter = M.ConverterClient(settings=settings)
        self.transcriber = M.TranscriberClient(settings=settings)
        self.js = job_service.JobService(settings=settings)
        self.file_manager = get_file_manager(settings)
        self._settings = settings

    def start_upload(self, client_id: str, language: str, file):

        """
        Creates a job from an uploaded file and puts it into the queue.

        The file is validated and saved to the shared folder here,
        because the worker can not get the file from the HTTP request.
        Returns job_id without the result (data = None).
        """

        language = validate_language(language)
        job_id = uuid.uuid4()
        try:
            self.js.create_document(job_id=job_id,
                                client_id=client_id,
                                source_type=JobSourceType.file,
                                )
            
        except Exception as e:
            raise AppError('CAN_NOT_CREATE_DOCUMENT') from e
        try:
            file_name = None
            size_bytes = file.size
            if size_bytes > self._settings.MAX_UPLOAD_MB * 1024 * 1024:  # check before reading, so a big file is not loaded into memory
               raise AppError("BIG_FILE")
            content = file.file.read()
            file.file.seek(0)
            validate_media_mime(content=content)
            file_extension = extract_extension(file.filename)
            tmp_path, file_name = self.file_manager.create_tmp_file_path(file_extension = file_extension)
            
            self.file_manager.save_to_tmp(tmp_path, content)
            self.js.update_document(job_id=job_id,
                            source = tmp_path,
                            filename=file_name
                                )
            validate_media_file(path=tmp_path)

        except Exception as e:
            self._fail_job(job_id, e)
            if file_name:
                self.file_manager.clear_temp_folders(file_name)
            raise

        from app.tasks import transcribe_upload_job  # imported here to avoid a circular import (tasks.py imports JobPipeline)
        transcribe_upload_job.delay(job_id = str(job_id),  # str: Celery sends arguments as JSON, UUID is not supported
               language = language, 
               tmp_path = tmp_path, 
               file_name = file_name, 
               file_extension = file_extension)
        return api_models.PostResponseData(job_id=job_id, data = None)
            

        

    def start_reference(self, data: api_models.SourceData):

        """
        Creates a job from an external source and puts it into the queue.

        Downloading is done later by the worker.
        Returns job_id without the result (data = None).
        """

        language = validate_language(data.language)
        job_id = uuid.uuid4()
        try:
            self.js.create_document(job_id=job_id,
                            client_id=data.client_id,
                            source_type=JobSourceType.reference,
                            source=data.source,
                            )
        except Exception as e:
            raise AppError('CAN_NOT_CREATE_DOCUMENT') from e
            #validate_media_mime(content=data.source)

        from app.tasks import transcribe_reference_job  # imported here to avoid a circular import (tasks.py imports JobPipeline)
        transcribe_reference_job.delay(job_id = str(job_id),
                                        source_type = data.source_type.value,  # .value: Enum is not JSON serializable
                                        source = data.source, 
                                        language = language)
        return api_models.PostResponseData(job_id=job_id, data = None)

        


    def run_reference(self, job_id: str, source_type: str, source: str, language: str):

        """
        Runs in the worker. Downloads the media from the source,
        then converts and transcribes it.

        On any error the job is marked as failed.
        Temporary files are removed in any case.
        """

        file_name = None  # set before try, so finally knows if there is something to clean
        try:
            self.js.update_document(job_id=job_id, job_status=JobStatus.processing)
            downloader_data = self.downloader.download(source=source, 
                                                source_type=source_type)
            file_name = downloader_data.file_name
            validate_media_file(path=downloader_data.file_path)
            self.js.update_document(job_id=job_id,
                            filename=downloader_data.file_name
                            )
            
            return self._process_file(job_id=job_id,
                                file_path = downloader_data.file_path,
                                file_name = downloader_data.file_name,
                                source_extension = downloader_data.file_extension,
                                language=language)
            
        except Exception as e:
            self._fail_job(job_id, e)
            raise
        finally:
            if file_name:
                self.file_manager.clear_temp_folders(file_name)


    def run_upload(self, job_id: str, language: str, tmp_path: str, file_name: str, file_extension: str):

        """
        Runs in the worker. Converts and transcribes the file
        that was saved by the gateway in start_upload.

        On any error the job is marked as failed.
        Temporary files are removed in any case.
        """

        try:
            self.js.update_document(job_id=job_id,
                                        job_status=JobStatus.processing
                                        )
            return self._process_file(job_id=job_id,
                                            file_path = tmp_path,
                                            file_name = file_name,
                                            source_extension = file_extension,
                                            language=language)
                                  
        except Exception as e:
            self._fail_job(job_id, e)
            raise
        finally:
            if file_name:
                self.file_manager.clear_temp_folders(file_name)
    


    def _process_file(self, job_id, file_path, file_name, source_extension, language):
        
        """
        Executes the common media processing workflow.

        Converts media to audio, sends it for transcription,
        updates job status, and stores the processing result.
        """

        converter_data = self.converter.convert(file_path = file_path,
                                                target_filename = file_name,
                                                source_extension = source_extension,
                                                target_extension = "wav")
            
        transcriber_data = self.transcriber.transcribe(file_path = converter_data.file_path,
                                                    file_name = converter_data.file_name,
                                                    target_extension = "txt",
                                                    language = language)
        self.js.update_document(job_id=job_id,
                        job_status=JobStatus.completed,
                        result_file_path=transcriber_data.file_path
                        )
        return api_models.PostResponseData(job_id=job_id, 
                                data = api_models.ResponseDataModel(result_url = transcriber_data.file_path))
    

    def _fail_job(self, job_id, error):
        
        """
        Updates the job state after a processing failure
        and stores error details for further investigation.
        """

        self.js.update_document(
            job_id=job_id,
            job_status=JobStatus.failed,
            error=build_job_error(error),
        )

