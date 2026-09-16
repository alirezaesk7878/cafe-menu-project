from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    available = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"))