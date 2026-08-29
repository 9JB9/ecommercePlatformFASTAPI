from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
import uvicorn

# database related imports
import models
from database import engine, Base, get_db
from routers import admins, orders, users
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Product
# def main():
#     print("Hello from ecommerceplatformfastapi!")

# create tables in database
Base.metadata.create_all(bind=engine)

# create app
app = FastAPI()

# mount other apps to URL path
# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/media", StaticFiles(directory="media"), name="media")


# # create router endpoints
# app.include_router(users.router, prefix="/api/users", tags=["users"])
# app.include_router(users.router, prefix="/api/posts", tags=["posts"])



#endpoints
@app.get("/feed") # feel free to change the naming, but this in reference to the main page scrollable feed
async def get_feed(db: Session = Depends(get_db)):
    """
        WE (yes we) ARE GOING TO TAKE THE SNEAKERS AND LOAD THEM UP AT THE LANDING PAGE...
        We can work out a proper load buffer later, but since we only have 180 sneakers to work with right now
        we can just go full caveman and load everything at once and doom scroll through all the listings
    """ 

    # let's start by pulling the data. We need a db session (GG)... and from there we need to actually access the data.

    sneakers = db.scalars(select(Product)).all()

    # Great! the front end will take this, pass it into a card component and render some nice things
    return {"Sneakers": sneakers}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)