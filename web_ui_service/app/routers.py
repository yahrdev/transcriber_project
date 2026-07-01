from flask import render_template, request, Response
import app.backend_service.gateway_client as gc


def register_routes(app, settings):
    """
    Registers web UI routes for uploading media files and downloading
    transcription results.

    The web UI service does not perform transcription itself.
    It receives user input from HTML forms and delegates processing
    to the API gateway service.
    """

    @app.route("/", methods=["GET"])
    def index():
        """
        Renders the main upload page.

        Returns:
            HTML page with:
            - video/audio file upload field;
            - language selector;
            - submit button for starting transcription.
        """
        return render_template("index.html")

    @app.route("/upload", methods=["POST"])
    def upload_file():
        """
        Handles media file upload from the web form.

        Expected form data:
            client_id (str):
                Identifier of the client submitting the request.
                For the web UI, usually "web-ui".

            language (str):
                Transcription language code, for example:
                - "uk" for Ukrainian;
                - "en" for English;
                - "ru" for Russian.

            file:
                Uploaded media file selected by the user.

        Flow:
            1. Reads uploaded file and form fields from the request.
            2. Validates that a file was provided.
            3. Sends the file to api_gateway_service through gateway_client.
            4. Receives job_id from the gateway.
            5. Renders the result page with a download link.

        Returns:
            200:
                HTML result page with download button.

            400:
                Plain text response if no file was uploaded.

            500:
                Unified JSON error response if gateway communication
                or internal processing fails.
        """
        uploaded_file = request.files.get("file")
        language = request.form.get("language")
        client_id = request.form.get("client_id")

        if uploaded_file is None or uploaded_file.filename == "":
            return "No file uploaded", 400

        job_id = gc.post_file(
            settings=settings,
            client_id=client_id,
            language=language,
            filename=uploaded_file.filename,
            file=uploaded_file,
            content_type=uploaded_file.content_type
        )

        return render_template(
            "result.html",
            job_id=job_id,
            download_url=f"/download/{job_id}"
        )

    @app.route("/download/<job_id>", methods=["GET"])
    def download_file(job_id):
        """
        Downloads the transcription result file for an existing job.

        Path parameters:
            job_id (str):
                Identifier of the transcription job returned after upload.

        Flow:
            1. Receives job_id from the URL.
            2. Requests the result file from api_gateway_service.
            3. Copies response body, status code, content type,
               and Content-Disposition header from the gateway response.
            4. Returns the file to the browser as a downloadable response.

        Returns:
            200:
                Text file with transcription result.

            4xx/5xx:
                Error response proxied or converted from gateway response.
        """
        gateway_response = gc.get_file(settings=settings, job_id=job_id)

        return Response(
            gateway_response.content,
            status=gateway_response.status_code,
            content_type=gateway_response.headers.get("content-type", "text/plain"),
            headers={
                "Content-Disposition": gateway_response.headers.get(
                    "content-disposition",
                    f'attachment; filename="transcription_{job_id}.txt"'
                )
            }
        )