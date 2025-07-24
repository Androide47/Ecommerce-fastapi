from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models.models import Blogs
from settings.database import engine, SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix="/blogs",
    tags=["blogs"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependencty = Annotated[dict, Depends(get_current_user)]

class BlogRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=3)
    author: str = Field(min_length=3, max_length=50)
    tags: str = Field(min_length=3)

@router.get("", status_code=status.HTTP_200_OK)
async def all_blogs(db: db_dependency):
    return db.query(Blogs).all()

@router.get("/{blog_id}", status_code=status.HTTP_200_OK)
async def single_blog(db: db_dependency, blog_id: int = Path(gt=0)):
    blog_model = db.query(Blogs).filter(Blogs.id == blog_id).first()
    if blog_model is not None:
        return blog_model
    raise HTTPException(status_code=404, detail="Blog not found")

@router.post("/new_blog", status_code=status.HTTP_201_CREATED)
async def create_blog(db: db_dependency, user: user_dependencty, blog_request: BlogRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    blog_model = Blogs(**blog_request.dict(), owner_id=user.get("id"))
    db.add(blog_model)
    db.commit()
    return blog_model

@router.put("/{blog_id}", status_code=status.HTTP_200_OK)
async def update_blog(db: db_dependency, user: user_dependencty, blog_request: BlogRequest, blog_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    blog_model = db.query(Blogs).filter(Blogs.id == blog_id).first()
    if blog_model is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    if blog_model.owner_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to update this blog")
    blog_model.title = blog_request.title
    blog_model.description = blog_request.description
    blog_model.content = blog_request.content
    blog_model.author = blog_request.author
    blog_model.tags = blog_request.tags
    db.commit()
    return blog_model

@router.delete("/{blog_id}", status_code=status.HTTP_200_OK)
async def delete_blog(db: db_dependency, user: user_dependencty, blog_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    blog_model = db.query(Blogs).filter(Blogs.id == blog_id).first()
    if blog_model is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    if blog_model.owner_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to delete this blog")
    db.query(Blogs).filter(Blogs.id == blog_id).delete()
    db.commit()
    return {"status": "success", "message": "Blog deleted successfully"}