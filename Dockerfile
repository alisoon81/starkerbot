# استفاده از ایمیج پایتون رسمی
FROM python:3.10-slim

# کپی کردن فایل‌ها به داخل کانتینر
WORKDIR /app
COPY . /app

# نصب پیش‌نیازها
RUN pip install --no-cache-dir -r requirements.txt

# فرمان اجرای ربات
CMD ["python", "bot.py"]
