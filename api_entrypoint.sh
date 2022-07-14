#!/bin/bash

echo "DEBUG=$DEBUG" > .env
echo "SECRET_KEY=$SECRET_KEY" >> .env
echo "ALLOWED_HOSTS=$ALLOWED_HOSTS" >> .env
echo "DB_NAME=$DB_NAME" >> .env
echo "DB_USER=$DB_USER" >> .env
echo "DB_PASSWORD=$DB_PASSWORD" >> .env
echo "DB_HOST=$DB_HOST" >> .env
echo "DB_PORT=$DB_PORT" >> .env
echo "API_KEY=$API_KEY" >> .env
echo "KAKAO_APPKEY=$KAKAO_APPKEY" >> .env
echo "KAKAO_REDIRECT_URI=$KAKAO_REDIRECT_URI" >> .env

# Migrate Database
python3 manage.py migrate --noinput

# Collect Staticfiles
python3 manage.py collectstatic --noinput

# Run Gunicorn (WSGI Server)
gunicorn --bind 0.0.0.0:8080 kolon_wecode.wsgi:application

nginx -g 'daemon off;'