# 使用官方 Python 运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 首先复制依赖列表文件，这可以利用Docker的缓存层加速后续构建
COPY backend/requirements.txt .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 将整个项目代码复制到容器中
COPY . .

# 声明容器运行时监听的端口（Railway会自动注入PORT环境变量）
EXPOSE 8000

# 启动 FastAPI 应用
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
