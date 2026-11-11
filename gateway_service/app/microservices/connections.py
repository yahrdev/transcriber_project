"""
Handles HTTP communication with external microservices.
"""


import requests
from pydantic import BaseModel, ValidationError
from typing import Type

from app.exceptions.exceptions import MicroserviceError, AppError
from app.models.common import Message


def create_and_post(
    request_model: BaseModel,
    response_model: Type[BaseModel],
    url: str,
    service_name: str,
    timeout: tuple = (20, 3600),
                    ) -> BaseModel:
    

    """
    Sends a request to a downstream microservice and validates
    the response against the expected schema.

    Network, serialization, and validation errors are converted
    to a unified application exception.
    """

    request_json = request_model.model_dump(mode="json")

    try:
        response = requests.post(url, json=request_json, timeout=timeout)
    except requests.RequestException as e:
        raise MicroserviceError(
            service=service_name,
            upstream_status_code=None,
            upstream_error_code="CONNECTION_ERROR",
            upstream_error_message=str(e),
            upstream_request=request_json
        )

    try:
        response_json = response.json()
    except ValueError as e:
        raise MicroserviceError(
            service=service_name,
            upstream_status_code=response.status_code,
            upstream_error_code="INVALID_JSON_RESPONSE",
            upstream_error_message=str(e),
            upstream_request=request_json
        )

    if response.ok:
        try:
            return response_model(**response_json)
        except ValidationError as e:
            raise MicroserviceError(
                service=service_name,
                upstream_status_code=response.status_code,
                upstream_error_code="RESPONSE_VALIDATION_ERROR",
                upstream_error_message=str(e),
                upstream_request=request_json
            )

    try:
        error_data = Message(**response_json)
        error_code = error_data.code
        error_message = error_data.message
    except ValidationError:
        error_code = "INVALID_ERROR_RESPONSE"
        error_message = str(response_json)

    raise MicroserviceError(
        service=service_name,
        upstream_status_code=response.status_code,
        upstream_error_code=error_code,
        upstream_error_message=error_message,
        upstream_request=request_json
    )