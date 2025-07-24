from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models.models import Blogs
from settings.database import engine, SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependencty = Annotated[dict, Depends(get_current_user)]

class NotificationRequest(BaseModel):
    user_id: int = Field(gt=0)
    message: str = Field(min_length=3)

@router.post("/new_notification", status_code=status.HTTP_201_CREATED)
async def create_notification(db: db_dependency, user: user_dependencty, notification_request: NotificationRequest):
    users_mails = db.query(Users).filter(Users.id == notification_request.user_id).first()
    if users_mails is None:
        raise HTTPException(status_code=401, detail="User not found")
    notification_model = Notifications(**notification_request.dict(), owner_id=user.get("id"))
    db.add(notification_model)
    db.commit()
    return notification_model