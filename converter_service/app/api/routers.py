"""
routers.py

The API routers. Details are provided in the Flasgger documentation.

"""


from flask import request, jsonify
from app.core.converter import get_convertator
from app.api.schemas import FilePathSchema, OutputSchema
from flasgger import swag_from
import os
import traceback


def register_routes(app, settings):
    @app.route("/convert", methods = ['POST'])
    @swag_from(os.path.join(settings.DOCS_DIR, "convert_file.yml"))
    def convert_file():
        result = FilePathSchema().load(request.get_json())
        convertator = get_convertator(result.source_extension, result.target_extension, settings)
        
        converted_obj = convertator.convert(input_path=result.file_path, 
                                            extension_from=result.source_extension, 
                                            file_name=result.target_filename, 
                                            extension_to=result.target_extension)
        converted_json = OutputSchema().dump(converted_obj)
        return jsonify(converted_json)


