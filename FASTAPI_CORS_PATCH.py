"""
Drop-in FastAPI CORS patch for hazm-tuwaiq-main backend.

Usage:
- Import and apply `enable_frontend_cors(app)` in your FastAPI app bootstrap
  right after creating `app = FastAPI(...)`.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def enable_frontend_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:4173",
            "http://localhost:4173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
