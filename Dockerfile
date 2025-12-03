FROM python:3.11-slim
WORKDIR /app
# 注意路径：从 my_porject/backend 复制
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 注意路径：复制整个 my_porject 文件夹的内容
COPY . .
EXPOSE 8000
# 启动命令路径不变，因为代码已被复制到 /app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
