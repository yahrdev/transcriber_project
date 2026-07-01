class TestSettings:
    @staticmethod
    def generate():
        class _Settings:
            HOST = "localhost"
            PORT = 7999
            BACKEND_PORT = 8000
            DEBUG_PROGRESS = False

            @property
            def http_base(self):
                return f"http://{self.HOST}:{self.BACKEND_PORT}"

        return _Settings()