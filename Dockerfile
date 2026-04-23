FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#agregar mount logs


COPY . .

ENV DJANGO_SETTINGS_MODULE=archivodjango.settings
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "archivodjango.wsgi:application"]

