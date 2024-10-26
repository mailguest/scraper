# 使用官方的 python:3.10-slim 版本作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 将当前目录下的内容复制到镜像的 /app 目录
COPY apis/ ./apis/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY utils/ ./utils/
COPY run.py .

# 复制 requirements.txt 文件
COPY requirements.txt .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建空的 data 和 logs 目录
RUN mkdir -p data logs

# 暴露 Flask 运行的端口（假设 Flask 运行在 5000 端口）
EXPOSE 5001

# 启动命令，使用传入的 data 和 logs 目录环境变量
CMD ["python", "run.py"]
