from multiprocessing.connection import wait
import time
import webbrowser
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException 

product_id = 'alpecin'
base_url = 'https://www.ah.nl/producten'

XPATH_BTN = "//button[@class='button-or-anchor_root__3z4hb button-default_root__2DBX1 button-default_primary__R4c6W']"
chrome_options = Options()
#chrome_options.add_argument('--headless')
browser = webdriver.Chrome(options=chrome_options, executable_path=r"chromedriver.exe")

from database import (
    create_item,
    update_item,
    remove_item,
)

def extract_products_cat(url):
    global content

    browser.get(url)

    try:
        ActionChains(browser).move_to_element(browser.find_element(By.XPATH, "//button[@id='accept-cookies']")).click().perform()
    except: NoSuchElementException

    #browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    ###### Wait until you see some element that signals the page is completely loaded
    #WebDriverWait(browser, timeout=10).until(lambda x: browser.find_element(By.XPATH, "//ul[@class='navigation-footer_icons__3aIpq']"))

    ############## do your things with the first page
    #content =  browser.page_source

    print("before scrolling: ")
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #### Now if you are sure there is next page
    # #browser.find_element(By.XPATH, "//span[@class='button-or-anchor_label__2eIdb']").click()


    while True:
        browser.implicitly_wait(1)
        try:
            ActionChains(browser).move_to_element(browser.find_element(By.XPATH,XPATH_BTN)).click().perform()    
        except NoSuchElementException:
            print("End: No next element found")
            break
        

    ##### Wait until you see some element that signals the page is completely loaded
    WebDriverWait(browser, timeout=10).until(lambda x: browser.find_element(By.XPATH, "//ul[@class='navigation-footer_icons__3aIpq']"))



    content =  browser.page_source.encode('ascii','ignore').decode("utf-8")

# with open('scraped.txt', 'w') as file:
#     file.write(content)



def get_categories():
    global catlist
    regex = re.compile('taxonomy-card_titleLink')
    catlist = []   
    soup = get_soup(base_url)

    for data in soup.find_all("a", {"class" : regex,  'href': True}):
        
        category = {
        'title': data.get_text(),
        'url': "https://www.ah.nl" + data.get("href") + "?page=26"
        }
        catlist.append(category)     
    return catlist

# get prices on current page
def get_prices(url):
    extract_products_cat(url)
    #soup = get_soup(content)
    prodlist = []
    regex = re.compile('link_root')
    regex2 = re.compile('price-amount_root')
    regex3 = re.compile('shield_title')
    regex4 = re.compile('shield_text')

    soup = BeautifulSoup(content, 'html.parser')
    
    productlist = soup.find_all("a", {"class": regex})
    #print(productlist)

    for item in productlist:
        #get price per item
        for price in item.find_all('div', class_= regex2):
            price = price.get_text()
            #get imgurl per item            
            img_url = item.find('img', class_='lazy-image_image__2025k').get('src')
            #check for possible discount, grab both title and text if available
            if (item.find('span', class_=regex3)):
                discount = item.find('span', class_=regex3).text
                if (item.find('span', class_=regex4)):
                    discount = (discount + " " + item.find('span', class_=regex4).text)
            else:
                discount = "0"
            #put into product obj
            product = {
                'product_name': item.get('title'),
                'price': price,
                'discount': discount,
                'img_url': img_url
            }
            #collect into list and resturn
            prodlist.append(product)
    print(create_item(prodlist))
    #store all products from category to DB

    #return to continue with next category
    
    #    # image = soup.find('img')['src']


async def store_items(prodlist):    
    response = await create_item(prodlist)()
    return response 


# link for extract html data
def get_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    htmldata = requests.get(url, headers=headers).text
    soup = BeautifulSoup(htmldata, 'html.parser')
    return soup


catlist = get_categories()
#print(catlist) 


#Goto first page of each category and grab all products, price, discounts
for cat in catlist:
    url = (cat['url'])
    prodlist = get_prices(url)

    


