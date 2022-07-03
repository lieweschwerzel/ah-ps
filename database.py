from ast import Subscript
from datetime import datetime
import re
from typing import Collection
from fastapi import HTTPException
from model import Item, Subscription
import pymongo
from pymongo import MongoClient
import motor.motor_asyncio

cluster = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://liewe:eaker007@cluster0.ohrbe.mongodb.net/test')
mongo_client = MongoClient('mongodb+srv://liewe:eaker007@cluster0.ohrbe.mongodb.net/test') 
#scan daily, each scan date has own collection
database = cluster["PriceTracker"]


def create_items(documents, scan_date):
    collection = database[scan_date] 
    print(get_time() + "  storing products in db")
    result = collection.insert_many(documents)
    return result
    


async def create_subscription(subscription):
    collection = database['subscriptions']     
    #collection.create_index([('email', pymongo.ASCENDING)], unique = True)    
    subs = []
    cursor  =  collection.find({ "$and" : [{"email": subscription.email}, {"product_name": subscription.product_name}]})
    #cursor  = collection.find({"email": subscription.email, "product_name": subscription.product_name})
    async for document in cursor:
        subs.append(Subscription(**document))
    if (len(subs) > 0):
        raise HTTPException(status_code=422, detail="subscription already exists") 
    else:
        await collection.insert_one(subscription.dict())
        return subscription


async def get_subscriptions(email):
    collection = database['subscriptions']  
    subscriptions = []
    cursor = collection.find({'email': email})
    async for document in cursor:
        subscriptions.append(Subscription(**document))
    return subscriptions

async def delete_subscription(email, product_name):
    collection = database['subscriptions']  
    collection.delete_one({ "$and" : [{"email": email}, {"product_name": product_name}]})

async def fetch_by_product_name(product_name):    
    collection = database['2022_07_03'] 
    items = []
    cursor = collection.find({'product_name': {"$regex" : product_name}})
    async for document in cursor:
        items.append(Item(**document))
    return items

async def fetch_all_items(scan_date):
    collection = database[scan_date] 
    items = []
    cursor = collection.find()
    async for document in cursor:
        items.append(Item(**document))
    return items

def set_last_updated(last_update):
    collection = database['_last_updated']  
    #create if it doesnt exist, else update the date
    collection.update_one({'id': 1}, {'$set':{'last_updated':last_update}}, upsert=True)  

def get_last_updated():
    collection = database['_last_updated']  
    res = collection.find({'id': 1})  
    return res

async def update_last_updated(last_update):
    collection = database['updates']    
    await collection.update_item({ title}, {"$set": {"mail": mail}})

# async def search(product):
#     collection = database[scan_date] 

#async def subscribe_to_product(email, productId):


def get_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S")



