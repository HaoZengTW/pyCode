FROM python:3.8
RUN apt-get update

RUN apt-get install python3-dev default-libmysqlclient-dev -y

COPY insert_db.py manage.py valve_response.xlsx requirements.txt /app/ 
COPY static /app/static
COPY mysite /app/mysite
COPY templates /app/templates
COPY website /app/website
WORKDIR /app 

RUN pip install -r requirements.txt

CMD sleep 15 && \
    python insert_db.py && \
    python manage.py migrate && \
    sleep 15 && \
    python manage.py runserver 0.0.0.0:8006