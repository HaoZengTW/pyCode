FROM python:3.11


WORKDIR /app 

RUN apt-get update \
    &&  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
    
RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata 

# 复制依赖文件
COPY requirements.txt /app/

# 安装 Python 依赖
RUN pip install -r requirements.txt

# 复制整个项目到容器
COPY . /app/

# 启动 Scrawling 脚本
CMD ["python", "scrawling_web.py"]
