"""
schemas.py

Data schemas and data validation

"""

from marshmallow import Schema, fields, post_load
from dataclasses import dataclass
from typing import Any



    
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
 