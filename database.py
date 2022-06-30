from datetime import datetime
from model import item
import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://liewe:eaker007@cluster0.ohrbe.mongodb.net/?retryWrites=true&w=majority")
#scan daily, each scan date has own collection
database = cluster["PriceTracker"]


def create_items(documents):
    scan_date = datetime.now().strftime("%Y_%m_%d")
    collection = database[scan_date] 
    print("Storing products in the db, collection: " + scan_date)
    result = collection.insert_many(documents)    
    return result


# def update_items(documents):
#     print(documents.product_name)
#     print(documents[0].product_name)
#     query = {"product_name": documents.product_name}
#     new_values = {"$set": {"price": documents.price, "discount": documents.discount , "img_url": documents.img_url}}

#     #update the document
#     result = collection.update_many(query, new_values)
#     return result

# async def remove_item(title):
#     await collection.delete_one({"title": title})
#     return True


# async def fetch_one_item(title):
#     document = await collection.find_one({"title": title})
#     return document

# async def  get_item_by_mail(mail):
#     document = await collection.find_one({"mail": mail})
#     return document

   
# async def fetch_all_items_by_mail(mail):
#     items = []
#     cursor = collection.find({"mail": mail})
#     async for document in cursor:
#         items.append(item(**document))
#     return items

# async def fetch_all_items():
#     items = []
#     cursor = collection.find()
#     async for document in cursor:
#         items.append(item(**document))
#     return items

# def get_time():
#     now = datetime.now()
#     return now.strftime("%H:%M:%S")