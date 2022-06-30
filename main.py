import schedule
import threading
import time
import fastapi
from fastapi import BackgroundTasks, FastAPI
from pricetracker import start_scrape
from database import fetch_all_items


# an HTTP-specific exception class  to generate exception information

from fastapi.middleware.cors import CORSMiddleware
HOUR_SCHEDULE = "15:35"
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

@app.get("/")
async def read_root():
    res = await fetch_all_items()
    return res

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