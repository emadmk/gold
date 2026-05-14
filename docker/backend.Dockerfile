FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev libxml2-dev libxslt1-dev libmagic1 \
    libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libffi-dev curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements/ /app/requirements/
ARG REQ=prod
RUN pip install -r requirements/${REQ}.txt

COPY backend/ /app/

RUN useradd -u 10001 -ms /bin/bash keyhan && chown -R keyhan:keyhan /app
USER keyhan

EXPOSE 8000
CMD ["gunicorn", "core.asgi:application", "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "4", "-b", "0.0.0.0:8000", "--access-logfile", "-"]
