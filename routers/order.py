from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import Annotated
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models.models import Products
from settings.database import engine, SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependencty = Annotated[dict, Depends(get_current_user)]

class OrderRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    total_price: float = Field(gt=0)
    user_id: int = Field(gt=0)
    public_id: str = Field(default="pending")
    order_id: int = Field(gt=0)
    order_status: str = Field(default="pending")
    order_date: datetime = Field(default=datetime.now())
    order_payment: str = Field(default="pending")
    order_shipping: str = Field(default="pending")
    order_address: str = Field(default="pending")
    order_traking_number: str = Field(default="pending")

@router.post("/create_order", status_code=status.HTTP_201_CREATED)
async def create_order(db: db_dependency, order_request: OrderRequest, user: user_dependencty):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    order_model = Products(**order_request.dict())
    db.add(order_model)
    db.commit()
    return {"message": "Order created successfully"}

@router.get("", status_code=status.HTTP_200_OK)
async def get_orders(db: db_dependency):
    return db.query(Products).all()

@router.get("/{order_id}", status_code=status.HTTP_200_OK)
async def get_order(db: db_dependency, order_id: int = Path(gt=0)):
    order_model = db.query(Products).filter(Products.id == order_id).first()
    if order_model is not None:
        return order_model
    raise HTTPException(status_code=404, detail="Order not found")

@router.put("/{order_id}", status_code=status.HTTP_200_OK)
async def update_order(db: db_dependency, order_request: OrderRequest, order_id: int = Path(gt=0), user: user_dependencty = None):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    order_model = db.query(Products).filter(Products.id == order_id).first()
    if order_model is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order_model.update(order_request.dict())
    db.commit()
    return {"message": "Order updated successfully"}

@router.delete("/{order_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_user)])
async def delete_order(db: db_dependency, order_id: int = Path(gt=0), user: user_dependencty = None):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    order_model = db.query(Products).filter(Products.id == order_id).first()
    if order_model is None:
        raise HTTPException(status_code=404, detail="Order not found")
    db.query(Products).filter(Products.id == order_id).delete()
    db.commit()
    return {"message": "Order deleted successfully"}