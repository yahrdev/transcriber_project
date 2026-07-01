"""
exceptions.py

Custom exception classes for the service.
"""

from app.exceptions.errors import ERROR_MESSAGES

class AppError(Exception):
    def __init__(self, code, **kwargs):
        self.code = code

        template = ERROR_MESSAGES.get(code)
        if template is None:
            self.message = f"Unknown error code: {code}"
        else:
            try:
                self.message = template.format(**kwargs)
            except KeyError as e:
                self.message = (
                    f"Invalid error template for code '{code}': "
                    f"missing format arg {e}"
                )

        super().__init__(self.message)


class MicroserviceError(Exception):
    def __init__(self, service, upstream_status_code, upstream_error_code, upstream_error_message, upstream_request):
        self.service = service
        self.upstream_status_code = upstream_status_code
        self.upstream_error_code = upstream_error_code
        self.upstream_error_message = upstream_error_message
        self.upstream_request=upstream_request
        self.code = 500
        self.message = "Internal Server Error"
        super().__init__(self.message)