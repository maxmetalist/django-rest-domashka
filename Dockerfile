FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY pyproject.toml poetry.lock* /app/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without dev --no-root

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]
