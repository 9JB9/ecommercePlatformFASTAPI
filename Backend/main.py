from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
import uvicorn

# database related imports
import models
from database import engine, Base, get_db
from routers import admins, orders, users

# def main():
#     print("Hello from ecommerceplatformfastapi!")

# create tables in database
Base.metadata.create_all(bind=engine)

# create app
app = FastAPI()

# mount other apps to URL path
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")


# create router endpoints
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(users.router, prefix="/api/posts", tags=["posts"])



#endpoints
@app.get("/feed") # feel free to change the naming, but this in reference to the main page scrollable feed
async def get_feed():
    


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)