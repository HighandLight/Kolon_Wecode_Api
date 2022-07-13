FROM python:3.9

RUN apt-get update && apt-get install netcat-openbsd -y

RUN pip install django

WORKDIR /usr/src/app

COPY requirements.txt ./ 

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000   

ENTRYPOINT /usr/share/entrypoint.sh