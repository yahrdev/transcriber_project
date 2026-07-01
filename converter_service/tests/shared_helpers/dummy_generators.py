"""
dummy_generators.py

Module for generating dummy files used in tests (e.g., video, text, PDF).
"""

import subprocess

def create_dummy_video(path):
    try:
        subprocess.run([
            "ffmpeg",
            "-f", "lavfi", "-i", "color=c=black:s=320x240:d=1",
            "-f", "lavfi", "-i", "anullsrc",
            "-shortest", path,
            "-y"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except:
        raise ValueError("Cannot generate dummy video")