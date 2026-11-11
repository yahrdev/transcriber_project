"""
validators.py

Utility functions for validating input values and checking URL format.
"""

from urllib.parse import urlparse


def is_url(filepath: str) -> bool:
        """
        Determines whether the provided string is a valid HTTP or HTTPS URL.
        """
        try:
            result = urlparse(filepath)
            return all([result.scheme in ("http", "https"), result.netloc])
        except Exception:
            return False