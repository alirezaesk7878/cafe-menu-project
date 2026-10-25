# منوی دیجیتال کافه

منوی دیجیتال با دسترسی از طریق QR Code و پنل مدیریت برای تغییر محصولات و قیمت‌ها.
ساخته‌شده با FastAPI و SQLite در بک‌اند و HTML/CSS/JavaScript در فرانت‌اند.

## اجرا

1. نصب کتابخانه‌ها:
   pip install -r requirements.txt

2. اجرای سرور:
   python -m uvicorn main:app --reload

3. مستندات و تست API:
   http://127.0.0.1:8000/docs

4. داده‌ی تستی (اختیاری):
   python seed.py

5. منوی مشتری: فایل front-end/index.html را با Live Server باز کنید.

6. پنل مدیریت: فایل front-end/admin.html را با Live Server باز کنید.
   نام کاربری و رمز پیش‌فرض: admin / admin1234
   برای تغییر، متغیرهای محیطی ADMIN_USERNAME و ADMIN_PASSWORD و SECRET_KEY را تنظیم کنید.

## QR Code

آدرس صفحه‌ی منو را در generate_qr.py عوض کنید (آی‌پی سیستم خودتان در شبکه) و اجرا کنید:
python generate_qr.py
گوشی و سیستم باید به یک شبکه وصل باشند.

## اندپوینت‌ها

بدون نیاز به ورود:
- GET /api/categories/
- GET /api/products/
- GET /api/products/{product_id}

فقط مدیر (نیاز به توکن):
- POST /api/auth/login/ (دریافت توکن)
- POST /api/categories/
- PUT /api/categories/{category_id}
- DELETE /api/categories/{category_id}
- POST /api/products/
- PUT /api/products/{product_id}
- DELETE /api/products/{product_id}