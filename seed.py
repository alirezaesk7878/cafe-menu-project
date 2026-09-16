from database import SessionLocal
import models

db = SessionLocal()

# دسته‌بندی‌ها
coffee = models.Category(name="قهوه")
dessert = models.Category(name="دسر")
db.add(coffee)
db.add(dessert)
db.commit()

# محصولات
db.add(models.Product(name="کاپوچینو", price=120000, description="قهوه با شیر", image_url="", available=True, category_id=coffee.id))
db.add(models.Product(name="اسپرسو", price=90000, description="قهوه غلیظ", image_url="", available=True, category_id=coffee.id))
db.add(models.Product(name="چیزکیک", price=150000, description="دسر خامه‌ای", image_url="", available=True, category_id=dessert.id))
db.commit()

db.close()
print("داده‌های تست با موفقیت اضافه شدن")