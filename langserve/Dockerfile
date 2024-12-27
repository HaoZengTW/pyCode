# 使用 Python Slim 基础镜像，减少镜像体积
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt /app/

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . /app/

# 开放 API 服务端口
EXPOSE 5000

# 启动服务
CMD ["python", "app.py"]
