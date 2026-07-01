"""
exceptions.py

Custom exception class for the service.
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