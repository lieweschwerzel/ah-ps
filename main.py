import schedule
import threading
from datetime import datetime, timedelta
import time
import fastapi
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pricetracker import start_scrape
from database import fetch_all_items


HOUR_SCHEDULE = "19:34:00"
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

@app.get("/{scan_date}")
async def scan_by_date(scan_date):
    res = await fetch_all_items(scan_date)
    return res

@app.get("/")
async def read_root():    
    return {"hi":"test"}

@app.on_event("startup")
async def startup_event():    
    print("******** Next scrape will be at: " + str(schedule.next_run()) +" ******** ")
    t = BackgroundTasks()
    t.start()

class BackgroundTasks(threading.Thread):        
    def run(self,*args,**kwargs):        
        while True:             
            schedule.run_pending()                    
            time.sleep(1)     


