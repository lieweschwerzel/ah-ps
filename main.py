import email
import re
import schedule
import threading
from datetime import datetime, timedelta
import time
import fastapi
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from model import Subscription
from pricetracker import start_scrape
from database import ( fetch_all_items, get_subscriptions, create_subscription, delete_subscription, fetch_by_product_name, check_discounts )


HOUR_SCHEDULE = "18:55:30"
schedule.every().day.at(HOUR_SCHEDULE).do(start_scrape)

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#post sub
@app.post("/post")
async def post_item(subscription: Subscription):
    response = await create_subscription(subscription)
    return response

@app.get("/subs/{email}")
async def get_subs_of_email(email):
    res = await get_subscriptions(email)
    return res

@app.delete("/subs/{email}/{product_name}")
async def delete_sub(email, product_name):    
    res = await delete_subscription(email, product_name)
    if res is None:
        return {"deleted"}
    return res

@app.get("/search/{product_name}")
async def search_by_product_name(product_name):
    res = await fetch_by_product_name(product_name)
    return res
    

@app.get("/scan_date/{scan_date}")
async def scan_by_date(scan_date):
    res = await fetch_all_items(scan_date)
    return res


@app.get("/")
async def read_root():    
    return {"hi":"test"}

@app.on_event("startup")
async def startup_event():
    await check_discounts("liewe")
    print("******** Next scrape will be at: " + str(schedule.next_run()) +" ******** ")
    t = BackgroundTasks()
    t.start()


class BackgroundTasks(threading.Thread):        
    def run(self,*args,**kwargs):        
        while True:                     
            schedule.run_pending()                    
            time.sleep(1)     


