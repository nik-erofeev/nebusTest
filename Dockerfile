FROM python:3.12-slim as production


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=10 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PYTHONPATH="/app"

WORKDIR /nebus

RUN apt-get update && \
    apt-get install -y curl postgresql-client && \
    apt-get clean


COPY pyproject.toml .
COPY poetry.lock .
COPY readme.md .


RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry install --no-root

COPY app/ ./app
COPY migrations/ ./migrations
COPY alembic.ini/ ./alembic.ini


COPY docker /nebus/docker
RUN chmod +x /nebus/docker/*


# указали в docker-compose
#CMD ["/bewise/docker/app.sh"]

EXPOSE 8000
