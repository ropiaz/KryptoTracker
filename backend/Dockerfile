FROM python:3.11
# Within the Docker container, outputs are output immediately, no buffering
ENV PYTHONENBUFFERED 1
# no creation of .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Working directory in container
WORKDIR /app/backend/
# Copy and install dependencies
COPY requirements.txt /app/backend/requirements.txt
RUN pip install -r requirements.txt
# Copy Bash-Script and change executable rights
COPY entrypoint.sh /app/backend/entrypoint.sh
RUN chmod +x /app/backend/entrypoint.sh
# Copy Django Project
COPY django_backend /app/backend/django_backend
# Start backend application with makemigrations, migrate and runserver
CMD ["/app/backend/entrypoint.sh"]