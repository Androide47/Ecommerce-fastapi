from fastapi import FastAPI
from sqlalchemy.orm import Session
from models.models import Base
from settings.database import engine
from routers import auth, blogs, notifications, products, order
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(blogs.router)
app.include_router(products.router)
app.include_router(order.router)
app.include_router(notifications.router)

# Entry point for the application

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)