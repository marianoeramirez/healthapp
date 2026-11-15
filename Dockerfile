FROM python:3.13-slim-bookworm

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN groupadd -g 1000 appgroup && \
    useradd -r -u 1000 -g appgroup appuser && \
    mkdir -p /data/media /data/staticfiles && \
    chown -R appuser:appgroup /usr/src/app /data && \
    chmod +x /usr/src/app/deploy/entrypoint.sh

# Entrypoint starts as root to fix /data volume ownership, then drops to appuser.
EXPOSE 8000

ENTRYPOINT ["/usr/src/app/deploy/entrypoint.sh"]
