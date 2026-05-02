FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py config.py models.py seed.py ./

# Bake the seeded SQLite DB into the image. Cloud Run filesystems are ephemeral,
# so each cold-start container will have the same deterministic seed data.
# Mutations persist for the life of the instance and reset when it scales to
# zero — acceptable for a demo
RUN python seed.py

# Cloud Run sets $PORT (default 8080). gunicorn must bind to it.
ENV PORT=8080
EXPOSE 8080

CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 60 app:app
