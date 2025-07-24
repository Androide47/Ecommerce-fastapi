from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models.models import Products
from settings.database import engine, SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependencty = Annotated[dict, Depends(get_current_user)]

class ProductRequest(BaseModel):
    name: str = Field(min_length=3)
    description: str = Field(min_length=3)
    price: float = Field(gt=0)
    stock: int = Field(gt=0)

@router.get("", status_code=status.HTTP_200_OK)
async def all_products(db: db_dependency):
    return db.query(Products).all()

@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def single_product(db: db_dependency, product_id: int = Path(gt=0)):
    product_model = db.query(Products).filter(Products.id == product_id).first()
    if product_model is not None:
        return product_model
    raise HTTPException(status_code=404, detail="Product not found")

@router.post("/new_product", status_code=status.HTTP_201_CREATED)
async def create_product(db: db_dependency, user: user_dependencty, product_request: ProductRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    product_model = Products(**product_request.dict(), owner_id=user.get("id"))
    db.add(product_model)
    db.commit()
    return product_model

@router.put("/{product_id}", status_code=status.HTTP_200_OK)
async def update_product(db: db_dependency, user: user_dependencty, product_request: ProductRequest, product_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    product_model = db.query(Products).filter(Products.id == product_id).first()
    if product_model is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if product_model.owner_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to update this product")
    product_model.name = product_request.name
    product_model.description = product_request.description
    product_model.price = product_request.price
    product_model.stock = product_request.stock
    db.commit()
    return product_model

@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(db: db_dependency, user: user_dependencty, product_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    product_model = db.query(Products).filter(Products.id == product_id).first()
    if product_model is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if product_model.owner_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to delete this product")
    db.query(Products).filter(Products.id == product_id).delete()
    db.commit()
    return {"message": "Product deleted successfully"}  