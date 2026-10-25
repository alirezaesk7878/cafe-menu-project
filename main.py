import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

# تنظیمات ادمین و توکن (برای نمونه‌کاره، برای کافه‌ی واقعی حتماً عوضشون کن)
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin1234")
TOKEN_HOURS = 8

bearer_scheme = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# چک می‌کنه درخواست توکن معتبر ادمین داره یا نه
def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["sub"]


# شکل داده‌هایی که از کاربر می‌گیریم
class LoginData(BaseModel):
    username: str
    password: str


class CategoryCreate(BaseModel):
    name: str


class ProductCreate(BaseModel):
    name: str
    price: int
    description: str | None = None
    image_url: str | None = None
    available: bool = True
    category_id: int


# برای ویرایش، همه‌ی فیلدها اختیاری‌ان
class ProductUpdate(BaseModel):
    name: str | None = None
    price: int | None = None
    description: str | None = None
    image_url: str | None = None
    available: bool | None = None
    category_id: int | None = None


# ---------- لاگین ----------

@app.post("/api/auth/login/")
def login(data: LoginData):
    user_ok = secrets.compare_digest(data.username.encode(), ADMIN_USERNAME.encode())
    pass_ok = secrets.compare_digest(data.password.encode(), ADMIN_PASSWORD.encode())
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=401, detail="Wrong username or password")

    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS)
    token = jwt.encode({"sub": data.username, "exp": expire}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


# ---------- خوندن (برای مشتری، بدون قفل) ----------

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


# ---------- ساخت، ویرایش، حذف (فقط ادمین) ----------

@app.post("/api/categories/", dependencies=[Depends(get_current_admin)])
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    category = models.Category(name=data.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@app.put("/api/categories/{category_id}", dependencies=[Depends(get_current_admin)])
def update_category(category_id: int, data: CategoryCreate, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    category.name = data.name
    db.commit()
    db.refresh(category)
    return category


@app.delete("/api/categories/{category_id}", dependencies=[Depends(get_current_admin)])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # اگه تو این دسته محصول هست، نمی‌ذاریم پاک بشه
    has_products = db.query(models.Product).filter(models.Product.category_id == category_id).first()
    if has_products:
        raise HTTPException(status_code=400, detail="Category has products, delete or move them first")

    db.delete(category)
    db.commit()
    return {"message": "Category deleted"}


@app.post("/api/products/", dependencies=[Depends(get_current_admin)])
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
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


@app.put("/api/products/{product_id}", dependencies=[Depends(get_current_admin)])
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # فقط فیلدهایی که فرستاده شده عوض می‌شن
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


@app.delete("/api/products/{product_id}", dependencies=[Depends(get_current_admin)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}