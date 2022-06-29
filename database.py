from model import item
import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://liewe:eaker007@cluster0.ohrbe.mongodb.net/?retryWrites=true&w=majority")

database = cluster["PriceTracker"]
collection = database["product"]

def create_item(documents):
    result = collection.insert_many(documents)
    print(result)
    return result

async def update_item(title, mail):
    await collection.update_one({"title": title}, {"$set": {"mail": mail}})
    document = await collection.find_one({"title": title})
    return document

async def remove_item(title):
    await collection.delete_one({"title": title})
    return True


async def fetch_one_item(title):
    document = await collection.find_one({"title": title})
    return document

async def  get_item_by_mail(mail):
    document = await collection.find_one({"mail": mail})
    return document

   
async def fetch_all_items_by_mail(mail):
    items = []
    cursor = collection.find({"mail": mail})
    async for document in cursor:
        items.append(item(**document))
    return items

async def fetch_all_items():
    items = []
    cursor = collection.find()
    async for document in cursor:
        items.append(item(**document))
    return items

