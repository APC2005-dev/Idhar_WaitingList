"""
Vercel entrypoint. Vercel's Python runtime looks for a WSGI-compatible
`app` object in this file — we just import the real one so there's a
single source of truth for the app's logic (app.py at the project root).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402,F401
