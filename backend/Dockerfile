FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN SECRET_KEY=build-only DB_PASSWORD=build-only python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "bankovni_kurzy.wsgi:application", \
     "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60"]
