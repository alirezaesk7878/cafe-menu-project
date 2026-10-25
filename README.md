# منوی دیجیتال کافه

## نحوه اجرا

1. نصب کتابخانه‌ها:
   pip install -r requirements.txt

2. اجرای سرور بک‌اند:
   python -m uvicorn main:app --reload

3. مستندات API:
   http://127.0.0.1:8000/docs

4. فرانت‌اند: فایل front-end/index.html را با Live Server باز کنید.

5. برای داده‌ی تستی (اختیاری):
   python seed.py

## اندپوینت‌ها

- GET /api/categories/
- GET /api/products/
- GET /api/products/{product_id}