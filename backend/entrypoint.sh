#!/bin/bash
python /app/backend/django_backend/manage.py makemigrations
python /app/backend/django_backend/manage.py migrate
python /app/backend/django_backend/manage.py runserver 0.0.0.0:8000