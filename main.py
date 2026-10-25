from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# شکل داده‌ای که موقع ساخت دسته‌بندی/محصول از کاربر می‌گیریم
class CategoryCreate(BaseModel):
    name: str


class ProductCreate(BaseModel):
    name: str
    price: int
    description: str | None = None
    image_url: str | None = None
    available: bool = True
    category_id: int


@app.get("/api/categories/")
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()


@app.get("/api/products/")
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()


@app.get("/api/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        return {"error": "Product not found"}
    return product


@app.post("/api/categories/")
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    category = models.Category(name=data.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@app.post("/api/products/")
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    # اول چک می‌کنیم دسته‌بندی‌ای که داده وجود داره
    category = db.query(models.Category).filter(models.Category.id == data.category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    product = models.Product(
        name=data.name,
        price=data.price,
        description=data.description,
        image_url=data.image_url,
        available=data.available,
        category_id=data.category_id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

# برای ویرایش، همه‌ی فیلدها اختیاری‌ان، هرکدوم رو فرستادی عوض می‌شه
class ProductUpdate(BaseModel):
    name: str | None = None
    price: int | None = None
    description: str | None = None
    image_url: str | None = None
    available: bool | None = None
    category_id: int | None = None


@app.put("/api/products/{product_id}")
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # فقط فیلدهایی که کاربر فرستاده رو عوض می‌کنیم
    changes = data.model_dump(exclude_unset=True)

    if "category_id" in changes:
        category = db.query(models.Category).filter(models.Category.id == changes["category_id"]).first()
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")

    for field, value in changes.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}


@app.put("/api/categories/{category_id}")
def update_category(category_id: int, data: CategoryCreate, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    category.name = data.name
    db.commit()
    db.refresh(category)
    return category


@app.delete("/api/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # اگه تو این دسته محصول هست، نمی‌ذاریم پاک بشه تا محصولات بی‌دسته نمونن
    has_products = db.query(models.Product).filter(models.Product.category_id == category_id).first()
    if has_products:
        raise HTTPException(status_code=400, detail="Category has products, delete or move them first")

    db.delete(category)
    db.commit()
    return {"message": "Category deleted"}