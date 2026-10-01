"""
Vercel Serverless Function entrypoint for AnthroFit OS (FastAPI)
"""
import os
import sys

# Ensure root directory is on Python module search path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from main import app
