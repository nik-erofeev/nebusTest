import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.templating import Jinja2Templates

from app.core.logger_config import configure_logging
from app.core.settings import AppConfig
from app.routes import router

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server...")

    yield

    logger.info("Shutting down server...")


def create_app(config: AppConfig) -> FastAPI:
    app = FastAPI(
        title=config.api.project_name,
        description=config.api.description,
        version=config.api.version,
        contact={"name": "Nik", "email": "example@example.com"},
        openapi_url=config.api.openapi_url,
        debug=config.api.echo,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.exception_handler(Exception)
    async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"An unexpected error occurred: {exc=!r}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred"},
        )

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

    templates = Jinja2Templates(directory=TEMPLATES_DIR)

    @app.get("/", tags=["Home"], include_in_schema=False)
    def home_page(request: Request) -> Response:
        logger.debug("Home page accessed")
        return templates.TemplateResponse(
            name="index.html",
            context={"request": request},
        )

    return app
