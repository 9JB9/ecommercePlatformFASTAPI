import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv() # I assume the .env would have to be in the same directory
              # loads the environment values from the environment file

api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
api_url = base_url + "/v3/stockx/products"
# now that we have the values, let's begin harvesting

SEARCH_QUERIES = { # the queries
    "jordan 1",
    "jordan 4",
    "nike dunk",
    "yeezy",
    "travis scott",
    "new balance 550",
    "adidas samba",
    "asics gel"
}

PAGES_PER_QUERY = 3 # the number of chunks of each limit size we will take
LIMITS_PER_PAGE = 25 # the number of items that will exist in each chunk (determined by page)

shoes_chosen = {}
async def harvest_data():
    print("Fetching sneaker data 🚀")

    # this api is more secure than other ones i have worked with in the past
    # we are going to need some headers for this


    headers = {
        "Authorization": f"{api_key}"
    }


    async with httpx.AsyncClient() as client:
        for query in SEARCH_QUERIES:
            print(f'\n🔍 Harvesting... -> {query}')

            for page in range(1, PAGES_PER_QUERY + 1): # you need
                parameters = {
                    "query": query,
                    "page": page,
                    "limit": LIMITS_PER_PAGE,
                    "sort": "rank"
                }

                try:
                    response = await client.get(api_url, headers=headers, params=parameters) # arguments specific to this method and not api
                    response.raise_for_status() # optional, but its here just to throw an error if it detects that any request went wrong
                    response_json = response.json() # turn the json data into usable object/dictionary
                    items = response_json.get('data')

                    for item in items:
                        # we should pull things by their unique ID, in order to minimize duplicates if they are present
                        # there are more measures that can be taken, but I don't mind some duplicates, it is what it is
                        shoe_id = item.get("id")
                        shoe_title = item.get("primary_title")
                        if shoe_id:
                            shoes_chosen[shoe_title] = item

                except:
                    print("something has gone wrong harvesting your data")
                    break # this is needed, bc if the query fails once, it will fail for the remaining pages too.

        # once we are done doing all the queries and everything we now have to get a proper listt
        # and then dump everything as a json

        sneaker_list = list(shoes_chosen.values())
        with open('sneakers.json', 'w') as file:
            json.dump(sneaker_list, file, indent=4)
            print("Successfully saved to sneakers.json! ✅")

if __name__ == "__main__":
    asyncio.run(harvest_data())
