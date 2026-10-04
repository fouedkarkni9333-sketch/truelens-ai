FROM python:3.10-slim

WORKDIR /app

# تثبيت الحزم النظامية اللازمة لمعالجة الصور والملفات
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# نسخ متطلبات المشروع وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع
COPY . .

# تعيين متغيرات البيئة الافتراضية
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# أمر التشغيل الافتراضي باستخدام Gunicorn
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "--worker-class", "uvicorn.workers.UvicornWorker", "wsgi:app"]
