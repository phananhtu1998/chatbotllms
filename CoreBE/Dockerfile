# Build stage
FROM python:3.11-alpine as builder

# Thiết lập working directory
WORKDIR /app

# Cài đặt các dependencies hệ thống cần thiết (gcc cho psycopg2)
RUN apk add --no-cache \
    build-base \
    postgresql-client \
    && rm -rf /var/cache/apk/*

# Copy requirements files
COPY requirements.txt .
COPY CoreBE/api/requirement.txt ./api_requirements.txt

# Cài đặt Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
    -r requirements.txt \
    -r api_requirements.txt \
    colorama \
    python-multipart \
    python-jose[cryptography] \
    passlib[bcrypt] \
    aiofiles \
    jinja2 && \

    # Xóa các file bytecode không cần thiết
    find /usr/local/lib/python3.11/site-packages -type d -name "__pycache__" -exec rm -rf {} + && \
    find /usr/local/lib/python3.11/site-packages -type f -name "*.pyc" -delete && \
    find /usr/local/lib/python3.11/site-packages -type f -name "*.pyo" -delete

# Production stage
FROM python:3.11-alpine as production

# Thiết lập các biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PYTHONHASHSEED=random \
    PYTHONIOENCODING=UTF-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /app

# Cài đặt các dependencies hệ thống cần thiết cho production
RUN apk add --no-cache \
    postgresql-client \
    curl \
    && rm -rf /var/cache/apk/*

# Copy các dependencies từ builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copy chỉ những file cần thiết và giữ nguyên cấu trúc thư mục
COPY CoreBE/api/ ./api/

# Tạo non-root user
RUN adduser -D appuser && \
    chown -R appuser:appuser /app && \
    # Xóa các file bytecode không cần thiết trong thư mục ứng dụng
    find /app -type d -name "__pycache__" -exec rm -rf {} + && \
    find /app -type f -name "*.pyc" -delete && \
    find /app -type f -name "*.pyo" -delete

# Chuyển sang non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command để chạy ứng dụng
CMD ["python", "api/main.py"] 