from datetime import datetime
from model import item
import pymongo
from pymongo import MongoClient
import motor.motor_asyncio

cluster = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://liewe:eaker007@cluster0.ohrbe.mongodb.net/test')

#cluster = MongoClient("mongodb+srv://liewe:eaker007@cluster0.ohrbe.mongodb.net/?retryWrites=true&w=majority")
#scan daily, each scan date has own collection
database = cluster["PriceTracker"]


def create_items(documents):
    scan_date = datetime.now().strftime("%Y_%m_%d")
    collection = database[scan_date] 
    print("Storing products in the db, collection: " + scan_date)
    result = collection.insert_many(documents)    
    return result


async def fetch_all_items():
    collection = database["2022_06_30"] 
    items = []
    cursor = collection.find()
    async for document in cursor:
        items.append(item(**document))
    return items

# def get_time():
#     now = datetime.now()
#     return now.strftime("%H:%M:%S")