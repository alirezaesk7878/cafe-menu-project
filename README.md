# منوی دیجیتال کافه — بخش نمایش منو

## نحوه اجرا

1. نصب کتابخانه‌ها:

cat > README.md << 'EOF'
# منوی دیجیتال کافه — بخش نمایش منو

## نحوه اجرا

1. نصب کتابخانه‌ها:


cat > README.md << 'EOF'
# منوی دیجیتال کافه — بخش نمایش منو

## نحوه اجرا

1. نصب کتابخانه‌ها:
pip install -r requirements.txt

2. اجرای سرور بک‌اند:
uvicorn main:app --reload

3. باز کردن مستندات API:
http://127.0.0.1:8000/docs

4. باز کردن فرانت‌اند:
فایل front-end/index.html را با Live Server باز کنید.

## اندپوینت‌ها

- GET /api/categories/
- GET /api/products/
- GET /api/products/{product_id}
