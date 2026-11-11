

"""
Handles HTTP communication with external microservices.
"""


import requests
from pydantic import ValidationError

from app.exceptions.exceptions import MicroserviceError
import app.backend_service.gateway_schemas as models
from typing import Literal
from urllib.parse import urljoin



def post_file(settings, client_id, language, filename, file, content_type):
    

    """
    Sends uploaded file to the API gateway and validates the response.

    Network, serialization, and validation errors are converted
    to a unified application exception.
    """
    url = urljoin(settings.http_base, "/jobs/upload")
    response = process_file(method="post", url = url, data={
                                                    "client_id": client_id,
                                                    "language": language,
                                                                        },
                                                                        files={
                                                                            "file": (filename, file, content_type)
                })
    return response.job_id

def get_file(settings, job_id):
    
    url=f"/jobs/{job_id}/result/download"
    url = urljoin(settings.http_base, url)
    return process_file(method="get", url=url)

def get_status(settings, job_id):

    """
    Requests the current job status from the API gateway.
    Used by the progress page for polling.
    """

    url=f"/jobs/{job_id}/status"
    url = urljoin(settings.http_base, url)

    response = process_file(method="get", url=url)
    return response.json()


   


def process_file(method: Literal["get", "post"], url, data = None, files = None):
    try:
        if method == "post":
            response = requests.post(url, data=data, files = files, timeout=(10, 3600))   
        elif method == "get":
            response = requests.get(url,  timeout=(10, 3600))

    except requests.RequestException as e:
        raise MicroserviceError(
            service="gateway",
            upstream_status_code=None,
            upstream_error_code="CONNECTION_ERROR",
            upstream_error_message=str(e),
            upstream_request={}
        )


    if method == "post":
        try:
            response_json = response.json()
        except ValueError as e:
            raise MicroserviceError(
                service="gateway",
                upstream_status_code=response.status_code,
                upstream_error_code="INVALID_JSON_RESPONSE",
                upstream_error_message=str(e),
                upstream_request={}
            )

    if response.ok:
        if method == "post":
            try:
                return models.PostResponseData(**response_json)
            except ValidationError as e:
                raise MicroserviceError(
                    service="gateway",
                    upstream_status_code=response.status_code,
                    upstream_error_code="RESPONSE_VALIDATION_ERROR",
                    upstream_error_message=str(e),
                    upstream_request={}
                )
        elif method == "get":
            return response


    if method == "get":
        try:
            response_json = response.json()
        except ValueError as e:
            raise MicroserviceError(
                service="gateway",
                upstream_status_code=response.status_code,
                upstream_error_code="INVALID_JSON_RESPONSE",
                upstream_error_message=str(e),
                upstream_request={}
            )
    try:
        error_data = models.Message(**response_json)
        error_code = error_data.code
        error_message = error_data.message
    except ValidationError:
        error_code = "INVALID_ERROR_RESPONSE"
        error_message = str(response_json)

    raise MicroserviceError(
        service="gateway",
        upstream_status_code=response.status_code,
        upstream_error_code=error_code,
        upstream_error_message=error_message,
        upstream_request={}
    )

