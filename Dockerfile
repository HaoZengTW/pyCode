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

# 設置 MySQL root 賬號密碼，並啟動 MySQL 服務和創建資料庫
# 設置 MariaDB root 賬號密碼，並啟動 MariaDB 服務和創建資料庫
# 初始化 MariaDB 並設置 root 賬號密碼

# CMD 啟動 MariaDB 和 Django 應用
CMD sleep 15 && \
    python manage.py migrate && \
    sleep 15 && \
    python manage.py runserver 0.0.0.0:8006