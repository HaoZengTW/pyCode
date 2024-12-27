# 使用 Python Slim 基础镜像，减少镜像体积
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app


# 复制依赖文件
COPY requirements.txt /app/

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制 Streamlit 应用代码
COPY . /app/

# 开放 Streamlit 默认端口
EXPOSE 8501

# 设置环境变量以禁用 Streamlit 的 CORS 限制（如果需要跨域）
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_PORT=8501

# 启动 Streamlit 应用
CMD ["streamlit", "run", "main.py"]
