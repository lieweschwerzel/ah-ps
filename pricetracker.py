from datetime import datetime
from multiprocessing.connection import wait
import sys
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException 
from database import (create_items, set_last_updated)


BASE_URL = 'https://www.ah.nl/producten'
chrome_options = Options()
chrome_options.add_argument('--headless')    
chrome_options.add_argument('--disable-gpu')
browser = webdriver.Chrome(options=chrome_options, executable_path=r"chromedriver.exe")    


def open_all_pages_cat(url, cat_name):
    NEXT_BTN_XPATH = "//button[@class='button-or-anchor_root__3z4hb button-default_root__2DBX1 button-default_primary__R4c6W']"
    browser.get(url)    
    try:
        ActionChains(browser).move_to_element(browser.find_element(By.XPATH, "//button[@id='accept-cookies']")).click().perform()
    except: NoSuchElementException    
    #scroll to END once to make Next button appear
    browser.implicitly_wait(2)
    starttime = datetime.now() 
    print(get_time() + "  collecting data from: "+ cat_name)    
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #### check if there is a next page button, click when available, break when not found
    while True:
        browser.implicitly_wait(1)
        try:     
            ActionChains(browser).move_to_element(browser.find_element(By.XPATH,NEXT_BTN_XPATH)).click().perform()
            #print(datetime.now().strftime("%H:%M:%S") + "  found next")    
        except NoSuchElementException:
            endtime = datetime.now()-starttime
            print(get_time() + "  end collecting data " + "( " + str(endtime)[0:7] + " )")
            break
    ##### Wait until you see some element that signals the page is completely loaded
    WebDriverWait(browser, timeout=10).until(lambda x: browser.find_element(By.XPATH, "//ul[@class='navigation-footer_icons__3aIpq']"))
    content =  browser.page_source.encode('ascii','ignore').decode("utf-8")
    return content


def get_categories():
    regex = re.compile('taxonomy-card_titleLink')
    catlist = []   
    # link for extract html data
    htmldata = requests.get(BASE_URL, headers = {'User-Agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(htmldata, 'html.parser')
    for data in soup.find_all("a", {"class" : regex,  'href': True}):        
        category = {
        'cat_name': data.get_text(),
        'url': "https://www.ah.nl" + data.get("href") + "?page=26"
        }
        catlist.append(category)     
    return catlist


# get all requiered info from page content from selenium
def get_product_info(content, scan_date):    
    #soup = get_soup(content)
    prodlist = []
    regex = re.compile('link_root') 
    regex2 = re.compile('price-amount_root')
    regex3 = re.compile('shield_title')
    regex4 = re.compile('shield_text')
    regex5 = re.compile('price_unitSize')
    soup = BeautifulSoup(content, 'html.parser')    
    productlist = soup.find_all("a", {"class": regex})
    #loop through the soup result per product 
    for item in productlist:
        #get price 
        for price in item.find_all('div', class_ = regex2):            
            #check for possible discount, grab both title (and text when available)      
            if (item.find('span', class_= regex3)):
                discount = item.find('span', class_= regex3).text
                if (item.find('span', class_= regex4)):
                    discount = (discount + " " + item.find('span', class_= regex4).text)
            else:
                discount = "0"
            if (item.find('span', class_ = regex5)):
                unit = item.find('span', class_ = regex5).text
            else: 
                unit = ("no unit")                
            #put into product obj
            product = {
                'product_name': item.get('title'),
                'price': price.get_text(),
                'unit': unit,
                'discount': discount,
                'img_url': item.find('img', class_ = 'lazy-image_image__2025k').get('src')
            }
            #collect into list and resturn
            prodlist.append(product)
    print(get_time() + "  found "+ str(len(prodlist)) + " products")
    #store all products from category to DB
    create_items(prodlist, scan_date)
    

def start_scrape():
    scan_date = datetime.now().strftime("%Y_%m_%d")    
    print()
    starttime = datetime.now()
    print(get_time() + "  start scraping...")
    #get all categories from ah.nl
    catlist = get_categories() 
    print(get_time() + "  received categories")
    #print(catlist) 
    #Goto first page of each category, use selenium to open all with click() and grab all products, price, discounts
    for cat in catlist:
        url = cat['url']
        cat_name = cat['cat_name']
        #open all pages until no more next button is found, with selenium since button is javascript
        content = open_all_pages_cat(url, cat_name)
        #use beautiful soup to extract relevant data and save to mongoDB
        get_product_info(content, scan_date) 
    endtime = datetime.now()-starttime
    print(get_time() + "  *** end of scraping. Total time: "+str(endtime)[0:7]+" ***")
    set_last_updated(scan_date)

def get_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S")




# with open('scraped.txt', 'w') as file:
#     file.write(content)