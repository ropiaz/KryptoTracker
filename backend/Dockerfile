FROM python:3.11
# Within the Docker container, outputs are output immediately, no buffering
ENV PYTHONENBUFFERED=1
# no creation of .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Working directory in container
WORKDIR /app/backend/
# Copy and install dependencies
COPY requirements.txt /app/backend/
RUN pip install -r requirements.txt
# Copy Bash-Script
COPY entrypoint.sh /app/backend/
# change CRLF to LF and change executable rights
RUN sed -i 's/\r$//' /app/backend/entrypoint.sh
RUN chmod +x /app/backend/entrypoint.sh
# Copy Django Project
COPY django_backend /app/backend/
# Start backend application with makemigrations, migrate and runserver
CMD ["/bin/sh", "-c", "/app/backend/entrypoint.sh"]