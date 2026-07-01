
A platform for extracting text from video and audio files.

## Microservices

The project consists of five microservices:

- **Downloader** – downloads input files.
- **Converter** – converts video to audio.
- **Transcriber** – transcribes audio into text.
- **Gateway** – controls the processing workflow.
- **Web UI** – provides the frontend interface.

## Technologies

- Python
- Flask
- FastAPI
- MongoDB
- Docker & Docker Compose
- GitHub Actions
- Pytest
- OpenAI Whisper API

## Project Structure

```
gateway_service/
converter_service/
downloader_service/
transcriber_service/
web_ui_service/
tests/
```

## Testing

The project includes:

- Unit tests
- Integration tests
- Automated CI checks using GitHub Actions

## Future Improvements

- Background task processing with Celery
- Asynchronous job execution
- Payment microservice
- Support for multiple transcription providers (e.g. local Whisper models and other APIs)
- Refactoring and architecture improvements
- Performance and scalability optimizations
