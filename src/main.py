from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import pandas as pd
import re
import html_to_json
import time
import os

def _init():
    options = Options()
    options.headless = True
    
    driver = webdriver.Chrome("C:/Users/MasterKaffe/Downloads/chromedriver.exe")#,options=options)
    driver.get("https://www.projectdiablo2.com/login")
    return driver


def _login(driver):
    wait = WebDriverWait(driver, 10)
    username = wait.until(EC.element_to_be_clickable((By.ID, "username")))
    password = driver.find_element_by_id("password")
    username.send_keys(os.environ['user'])
    password.send_keys(os.environ['password'])
    driver.find_element_by_xpath("//*[contains(concat( ' ', @class, ' ' ), concat( ' ', 'primary', ' ' ))]").click()
    time.sleep(2)


def _search_for_item(driver, item_name, include_offline=True):
    driver.get("https://www.projectdiablo2.com/trade")
    
    label = driver.find_element_by_xpath("//label[contains(text(), 'Name')]") 
    dynamic_input_id = re.search(r"input-(.*?)\"",label.get_attribute('outerHTML')).group(0)[:-1]
    name_search = driver.find_element_by_id(dynamic_input_id)
    
    name_search.send_keys(item_name)
    driver.find_element_by_xpath("//*[@id='app']/div[2]").click()
    if include_offline:
        driver.find_element_by_xpath("//*[@id='app']/div[1]/main/div/div/div/div/div[2]/div[1]/div/div/div/div[5]/div/div/div[4]/div/div/div/div/div[1]/div/div[1]").click()
    driver.find_element_by_xpath("//span[contains(text(), 'Search')]").click()
    time.sleep(1)
    return driver

def _get_raw_listings(driver):
    container=driver.find_element_by_xpath("//*[@id='app']/div[1]/main/div/div/div/div/div[2]/div[2]")
    raw_data = container.get_attribute("outerHTML")
    return raw_data

#TODO: cleanup attributes as separate
def _fetch_clean_data(driver, raw_data, listings_clean):
    raw_data = html_to_json.convert(raw_data)
    listings=raw_data['div'][0]['div'][0]['div'][:-1]
    err=[]
    for listing in listings:
        listing_details = listing['div'][0]['div'][0]['div'][0]['div'][0]['div'][0]['div'][0]['div'][2]['div']
        item_attributes = listing_details[0]['div']
        ask_price = listing_details[1]['div'][0]['div'][0]['span'][1]['_value']
        att = ''
    
        for att_json in item_attributes:
            if 'span' in att_json['div'][0]:
                att = att + ' /// ' + att_json['div'][0]['span'][0]['_value']
                
            elif '_value' in att_json['div'][0]: #sockets
                sockets = re.findall(r'\d+',att_json['div'][0]['_value'])
                if sockets:
                    att = att + ' /// ' + 'Sockets:' + sockets[0]
            else:
                err.append(att_json)
                continue
        
        listings_clean.append({'attributes': att,'ask_price': ask_price})
    return listings_clean, err

def _next_page(driver):
    for n in [10,9,8,7,6,5,4,3]:
        try:
            page_indicator = driver.find_element_by_xpath("//*[@id='page-top']/div[11]/div/nav/ul/li["+str(n)+"]/button")
            page_indicator.click()
        except:
            continue
        
def main_scraper(driver):
    listings_clean = []
    list_temp = []
    list_cache=[]
    while True:
        raw_data = _get_raw_listings(driver)
        list_temp = []
        list_temp, _ = _fetch_clean_data(driver, raw_data, list_temp)
        if list_temp == list_cache:
            break
        
        listings_clean = listings_clean + list_temp
        list_cache = list_temp
        _next_page(driver)
        time.sleep(0.5)    
    
    return pd.DataFrame(listings_clean)
        
driver = _init()
_login(driver)   
_search_for_item(driver, "Stone Of Jordan")
all_listings = main_scraper(driver)
