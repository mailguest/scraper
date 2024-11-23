# 使用官方的 python:3.10-slim 版本作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 创建所需的目录结构
RUN mkdir -p scripts static templates utils apis config data logs

# 复制项目文件到对应目录
COPY scripts/ ./scripts/
COPY static/ ./static/
COPY templates/ ./templates/
COPY utils/ ./utils/
COPY apis/ ./apis/
COPY config/ ./config/
COPY run.py .
COPY requirements.txt .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 Flask 运行的端口
EXPOSE 5001

# 启动命令
CMD ["python", "run.py"]
