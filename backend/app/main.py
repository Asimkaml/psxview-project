from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.routes import auth as auth_routes
from app.api.routes import health as health_routes


settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

# Basic CORS configuration for local development; tighten in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth_routes.router, prefix=settings.API_V1_PREFIX)
