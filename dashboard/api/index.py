from flask import Flask, Request
import sys
import os

# Add the root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app

def handler(request: Request):
    """Handle requests in Vercel serverless function"""
    def start_response(status, headers, exc_info=None):
        def write(body):
            pass  # No-op for serverless
        return write

    return flask_app.wsgi_app(request.environ, start_response)
