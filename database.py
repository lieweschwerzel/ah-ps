from ast import Subscript
from datetime import datetime
from gc import collect
from itertools import product
import re
from tokenize import Double
from typing import Collection
from fastapi import HTTPException
from model import Item, Subscription
import pymongo
from pymongo import MongoClient
import motor.motor_asyncio
import psycopg2 

cluster = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://liewe:eaker007@cluster0.ohrbe.mongodb.net/test')
mongo_client = MongoClient('mongodb+srv://liewe:eaker007@cluster0.ohrbe.mongodb.net/test') 
#scan daily, each scan date has own collection
database = cluster["PriceTracker"]

try:
    connection = psycopg2.connect("dbname=product user=liewe password=liewe")
    # Create a cursor to perform database operations
    cursor = connection.cursor()
    # Print PostgreSQL details
    print("PostgreSQL server information")
    print(connection.get_dsn_parameters(), "\n")
    # Executing a SQL query
    cursor.execute("SELECT * FROM subscription")
    print(cursor.fetchone())
    # Fetch result
    record = cursor.fetchone()
    print("You are connected to - ", record, "\n")

except (Exception) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

def create_item_postgres(documents, scan_date):
    connection = psycopg2.connect("dbname=product user=liewe password=liewe")
    # Create a cursor to perform database operations
    cursor = connection.cursor()
    #Creating table as per requirement
    sql ='''CREATE TABLE IF NOT EXISTS product(
    id SERIAL PRIMARY KEY,           
    product_name CHAR(500) NOT NULL,
    price CHAR(20),
    unit CHAR(20),
    discount CHAR(60),
    img_url CHAR(300)
    )'''
    cursor.execute(sql)
    print("Table created successfully........")
    connection.commit()
    
    print(scan_date)
    print(get_time() + "  storing products in db")
    for d in documents:
        keyvalues = list(d.items())
        product_name = keyvalues[0][1]
        price = keyvalues[1][1]
        unit = keyvalues[2][1]
        discount = keyvalues[3][1]
        img_url = keyvalues[4][1]
        
        add_product = ("INSERT into product (product_name, price, unit, discount, img_url) VALUES (%s, %s, %s, %s, %s)")
        insert_data = (product_name, price, unit, discount, img_url)
        cursor.execute(add_product, insert_data)
        connection.commit()

    cursor.close()
    connection.close()


def create_items(documents, scan_date):
    collection = database[scan_date] 
    
    result = collection.insert_many(documents)
    return result
    


async def create_subscription(subscription):
    collection = database['subscriptions']     
    #collection.create_index([('email', pymongo.ASCENDING)], unique = True)    
    subs = []
    #check if sub already exists
    cursor  =  collection.find({ "$and" : [{"email": subscription.email}, {"product_name": subscription.product_name}, {"unit": subscription.unit}]})
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
    collection = database['2022_07_09'] 
    items = []
    regex = ".*" + product_name + ".*"
    cursor = collection.find({'product_name': re.compile(regex, re.IGNORECASE)}).limit(15)
    async for document in cursor:
        items.append(Item(**document))
    return items

async def fetch_all_items(scan_date):
    collection = database[scan_date] 
    items = []
    cursor = collection.find()
    async for document in cursor:
        document.toLowerCase()
        items.append(Item(**document))
    return items

def set_last_updated(last_update):
    collection = database['_last_updated']  
    #create if it doesnt exist, else update the date
    collection.update_one({'id': 1}, {'$set':{'last_updated':last_update}}, upsert=True)  

async def last_updated_db():
    collection = database['_last_updated']  
    return await collection.find_one({'id' : 1})
  

 
async def check_discounts(email):
    collection = database['subscriptions']
    cursor = collection.find({'email': email}) 
    subs = []
    async for doc in cursor:
        subs.append(Subscription(**doc))
    print(len(subs))
    for sub in subs:
        print(sub.product_name)
    # check if latest db collection has product with discount not null and send email (or add to a list and send later all at once by mail)
    
    # 

def get_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S")



