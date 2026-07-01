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
    def __init__(self, settings):
        self.downloader = M.DownloaderClient(settings=settings)
        self.converter = M.ConverterClient(settings=settings)
        self.transcriber = M.TranscriberClient(settings=settings)
        self.js = job_service.JobService(settings=settings)
        self.file_manager = get_file_manager(settings)



    def process_reference(self, data: api_models.SourceData):

        """
        Processes a job created from an external media reference.

        The media file is downloaded first and then passed through
        the standard processing pipeline.
        """

        language = validate_language(data.language)
        job_id = uuid.uuid4()
        try:
            self.js.create_document(job_id=job_id,
                            client_id=data.client_id,
                            source_type=JobSourceType.reference,
                            source=data.source,
                            )
        except: 
             raise AppError('CAN_NOT_CREATE_DOCUMENT')
        try:
            file_name = None
            #validate_media_mime(content=data.source)
            self.js.update_document(job_id=job_id,
                            job_status=JobStatus.processing
                            )
            
            downloader_data = self.downloader.download(source=data.source, 
                                                source_type=data.source_type)
            file_name = downloader_data.file_name
            validate_media_file(path=downloader_data.file_path)
            self.js.update_document(job_id=job_id,
                            filename=downloader_data.file_name
                            )
            
            return self._process_file(job_id=job_id,
                                file_path = downloader_data.file_path,
                                file_name = downloader_data.file_name,
                                source_extension = downloader_data.file_extension,
                                language=data.language)
            
        except Exception as e:
            self._fail_job(job_id, e)
            raise
        finally:
            if file_name:
                self.file_manager.clear_temp_folders(file_name)
        


    def process_upload(self, client_id: str, language: str, file):

        """
        Processes a job created from an uploaded file.

        The uploaded content is validated, stored temporarily,
        and then passed through the standard processing pipeline.
        """

        language = validate_language(language)
        job_id = uuid.uuid4()
        try:
            self.js.create_document(job_id=job_id,
                                client_id=client_id,
                                source_type=JobSourceType.file,
                                )
            
        except: 
             raise AppError('CAN_NOT_CREATE_DOCUMENT')
        try:
            file_name = None
            content = file.file.read()
            file.file.seek(0)
            validate_media_mime(content=content)
            self.js.update_document(job_id=job_id,
                                job_status=JobStatus.processing
                                )
            file_extension = extract_extension(file.filename)
            tmp_path, file_name = self.file_manager.create_tmp_file_path(file_extension = file_extension)
            
            self.file_manager.save_to_tmp(tmp_path, content)
            self.js.update_document(job_id=job_id,
                            source = tmp_path,
                            filename=file_name
                                )
            validate_media_file(path=tmp_path)
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
                                                target_extension = "mp3")
            
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

