
"""
Provides CRUD operations for job documents in MongoDB.
"""


from app.models.job_schemas import Job
from app.exceptions.exceptions import AppError
from app.db.client import generate_db

class Jobs_Collection:

    def __init__(self, settings):
        self.jobs_collection = generate_db(settings=settings)


    def insert(self, job: Job):
        self.jobs_collection.insert_one(job.model_dump(mode="json"))

    def update(self, job_id: str, **fields):
        fields = {k: v for k, v in fields.items() if v is not None}

        if not fields:
            return

        result = self.jobs_collection.update_one(
            {"job_id": str(job_id)},
            {"$set": fields}
        )

        if result.matched_count == 0:
            raise AppError("JOB_NOT_FOUND", job_id=str(job_id))


    def get(self, job_id):
        query = {"job_id": str(job_id)}
        document = self.jobs_collection.find_one(query) #dict or None
        if document:
            return Job.model_validate(document)
        else:
            raise AppError("JOB_NOT_FOUND", job_id=str(job_id)) 