"""
schemas.py

Data schemas and data validation

"""

from marshmallow import Schema, fields, post_load, validates
from marshmallow.validate import Length
from dataclasses import dataclass
from app.exceptions.exceptions import AppError
import app.core.allowed_conversions as ac
from typing import Optional, Any

@dataclass
class FilePath:

    """
    convert_file endpoint JSON
    """

    file_path: str
    target_filename: str
    target_extension: str
    source_extension: Optional[str] = None



class FilePathSchema(Schema):
    file_path = fields.Str(required=True, validate=Length(min=1))
    target_filename = fields.Str(required=True, validate=Length(min=1))
    target_extension = fields.Str(required=True, validate=Length(min=1))
    source_extension = fields.Str(required=True,validate=Length(min=1))

    @post_load
    def make_parameter(self, data, **kwargs):

        """
        Allows to work with schema fields instead of raw JSON.
        """

        return FilePath(**data)
    

    @validates("source_extension")
    def validate_source_extension(self, value):
        if value:
            check_supported_extensions(value)
       
    
    @validates("target_extension")
    def validate_target_extension(self, value):
        check_supported_extensions(value)

    
@dataclass
class Message:
    message: Any  
    code: str

class MessageSchema(Schema):
    message = fields.Raw(data_key="message")
    code = fields.Str(data_key="code")

    @post_load
    def make_parameter(self, data, **kwargs):
        return Message(**data)
    
@dataclass
class Output:
    file_path: str
    file_name: str
    file_extension: str

class OutputSchema(Schema):
    file_path = fields.Str()
    file_name = fields.Str()
    file_extension = fields.Str()

    @post_load
    def make_parameter(self, data, **kwargs):
        return Output(**data)


def check_supported_extensions(value: str):
    """
    Check whether the received extensions are supported and correct.
    """
    supported_exts = {
                exc
                for conversions in ac.Allowed_conversions.values()
                for pair in conversions
                for exc in pair
    }
    if value.lower() not in supported_exts:
        raise AppError("UNSUPPORTED_EXTENSION", value = value, supported = ', '.join(supported_exts))


