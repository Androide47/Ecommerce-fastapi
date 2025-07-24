from settings.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Numeric, TIMESTAMP, func

class Products(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String)
    description = Column(String)
    price = Column(Integer)
    available = Column(Boolean, default=True)
    quantity = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))

class Blogs(Base):
    __tablename__ = 'blogs'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    content = Column(String)
    author = Column(String)
    tags = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String)
    total_amount = Column(Numeric(10, 2))
    order_date = Column(TIMESTAMP, server_default=func.now())
    status = Column(String, default="pending")
    shipping_address = Column(String)
    shipping_cost = Column(Numeric(10, 2))
    tracking_number = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
