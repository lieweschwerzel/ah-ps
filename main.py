from multiprocessing.connection import wait
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException 
from database import (create_items)
    

def open_all_pages_cat(url, cat_name):
    NEXT_BTN_XPATH = "//button[@class='button-or-anchor_root__3z4hb button-default_root__2DBX1 button-default_primary__R4c6W']"
    browser.get(url)    
    try:
        ActionChains(browser).move_to_element(browser.find_element(By.XPATH, "//button[@id='accept-cookies']")).click().perform()
    except: NoSuchElementException
    print("Start collecting data from: "+ cat_name)
    #scroll to END once to make Next button appear
    browser.implicitly_wait(2)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #### check if there is a next page button, click when available, break when not found
    while True:
        browser.implicitly_wait(1)
        try:
            ActionChains(browser).move_to_element(browser.find_element(By.XPATH,NEXT_BTN_XPATH)).click().perform()    
        except NoSuchElementException:
            print("Ended collecting data from: "+ cat_name)
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
def get_product_info(content):    
    #soup = get_soup(content)
    prodlist = []
    regex = re.compile('link_root')
    regex2 = re.compile('price-amount_root')
    regex3 = re.compile('shield_title')
    regex4 = re.compile('shield_text')

    soup = BeautifulSoup(content, 'html.parser')    
    productlist = soup.find_all("a", {"class": regex})
    #loop through the soup result per product 
    for item in productlist:
        #get price 
        for price in item.find_all('div', class_= regex2):            
            #check for possible discount, grab both title (and text when available)
            if (item.find('span', class_=regex3)):
                discount = item.find('span', class_=regex3).text
                if (item.find('span', class_=regex4)):
                    discount = (discount + " " + item.find('span', class_=regex4).text)
            else:
                discount = "0"
            #put into product obj
            product = {
                'product_name': item.get('title'),
                'price': price.get_text(),
                'discount': discount,
                'img_url': item.find('img', class_='lazy-image_image__2025k').get('src')
            }
            #collect into list and resturn
            prodlist.append(product)
    print(str(len(prodlist))+ (" products found \nStoring products in the db" ))
    #store all products from category to DB
    create_items(prodlist)

if __name__ == "__main__":
    BASE_URL = 'https://www.ah.nl/producten'
    chrome_options = Options()
    chrome_options.add_argument('--headless')    
    browser = webdriver.Chrome(options=chrome_options, executable_path=r"chromedriver.exe")
  
    #get all categories from ah.nl
    catlist = get_categories()
    #print(catlist) 
    #Goto first page of each category, use selenium to open all with click() and grab all products, price, discounts
    for cat in catlist:
        url = (cat['url'])
        cat_name = (cat['cat_name'])
        #open all pages until no more next button is found, with selenium since button is javascript
        content = open_all_pages_cat(url, cat_name)
        #use beautiful soup to extract relevant data and save to mongoDB
        get_product_info(content) 


# with open('scraped.txt', 'w') as file:
#     file.write(content)