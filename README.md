# KryptoTracker

## Student Research Project @ DHBW Mannheim
Description: tba

## Features
tba

## Install Guide
### Frontend
- Navigate to React directory  ```cd /frontend/react_webapp```
- Install dependencies for React: ```npm install```
- Start React application in: ```npm start```
- Webpage should be available on ```localhost:3000```

### Backend
- Django, MySQL and PhpMyAdmin in docker containers
- Run docker containers in root directory: ```docker-compose up -d```
- Django Backend should be available on Port 8000: ```localhost:8000```
- PhpMyAdmin should be available on Port 8080: ```localhost:8080```

#### Superuser
If necessary create a superuser: 
- ```docker exec -it <container-name> bash```
- ```cd django_backend```
- ```python manage.py createsuperuser```

