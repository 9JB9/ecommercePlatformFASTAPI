"""
    This file is going to do some seeding.. we are going to fill up the Product table in the database.
    There is currently nothing in it, so we need to make the sneakers.json data usable.
"""
import json # so python can interact with the JSON
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR)) # so database/models are importable regardless of cwd

from database import SessionLocal, engine, Base # the stuff we need from the database
from models import Product # the actual table we need to work with
    
Base.metadata.create_all(bind=engine) # will check the database and create anything that hasn't been created yet
db = SessionLocal()

def seedDB (): # doesn't need to be async, we are running this once and never touching it again... also separate from the main application
    with open(BACKEND_DIR / 'sneakers.json', 'r', encoding='utf-8') as file:
        sneaker_data = json.load(file) # the data exists outside of this block (I'm too Java brained, scope is different in python)

    print("Beginning the seeding, stand by... 🌱")

    for sneaker in sneaker_data: 
        product = Product(
            name=sneaker.get("title"),
            brand=sneaker.get("brand"),
            price=sneaker.get("avg_price"),# sadly current_price isn't available, I think there is a way to get live pricing with KicksDB
                                           # but that would require constant pinging of their API, and I don't get paid enough to pay for their
                                           # premium API services (I am broke)
            image_url=sneaker.get("image"),
            gender=sneaker.get("gender"),
            description=sneaker.get("description"),
            link=sneaker.get("link")
        )
        db.add(product)
        print(f"Successfully added {sneaker.get("title")} to the DB ✅")
    db.commit()
    db.close() # couldn't this also be written outside the function and have this still work?

if __name__ == "__main__":
    seedDB()
        
