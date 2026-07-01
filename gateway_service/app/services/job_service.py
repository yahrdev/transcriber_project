"""
Provides business logic for job management.
"""


from datetime import datetime
import app.models.job_schemas as job_models

class JobService:
    def __init__(self, settings):
        from app.db.job_repository import Jobs_Collection
        self.job_db = Jobs_Collection(settings=settings)

    def get_file_path_name_by_job_id(self, job_id):
        job = self.job_db.get(job_id=job_id)
        return job.result_file_path, job.file_name
    
    def get_job_status(self, job_id):
        job = self.job_db.get(job_id=job_id)
        return job.status

    def create_document(self, job_id, client_id = None, source_type: job_models.JobSourceType = None, source = None):
        self.job_id = job_id
        NewJob = job_models.Job(job_id=job_id, 
                        client_id=client_id, 
                        status=job_models.JobStatus.pending, 
                        source_type=source_type,
                        source=source,
                        file_name="",
                        result_file_path="",
                        error=job_models.JobError(), 
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                        )
        self.job_db.insert(NewJob)
        

    def update_document(self, job_id, source: str = None, filename: str = None, job_status: job_models.JobStatus = None, result_file_path: str = None, error: job_models.JobError = None):
        self.job_db.update(job_id=job_id,
            file_name = filename,
            source = source,
            updated_at = datetime.utcnow(),
            status = job_status,
            result_file_path = result_file_path, 
            error = error.model_dump(mode="json") if error else None
        )




