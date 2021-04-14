from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import html_to_json
import time
import os

def _init():
    options = Options()
    options.headless = True
    
    driver = webdriver.Chrome("chromedriver.exe")
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
    return driver

def _scrape_item(driver, item_name):
    driver.get("https://www.projectdiablo2.com/trade")
    
    label = driver.find_element_by_xpath("//label[contains(text(), 'Name')]") 
    dynamic_input_id = re.search(r"input-(.*?)\"",label.get_attribute('outerHTML')).group(0)[:-1]
    name_search = driver.find_element_by_id(dynamic_input_id)
    
    name_search.send_keys(item_name)
    driver.find_element_by_xpath("//*[@id='app']/div[2]").click()
    driver.find_element_by_xpath("//span[contains(text(), 'Search')]").click()

    time.sleep(1)
    container=driver.find_element_by_xpath("//*[@id='app']/div[1]/main/div/div/div/div/div[2]/div[2]")
    data = container.get_attribute("outerHTML")
    return driver, data

driver = _init()
driver = _login(driver)   
driver, data = _scrape_item(driver, "Stone Of Jordan")

data = html_to_json.convert(data)
listings=data['div'][0]['div'][0]['div'][:-1]
err=[]
for listing in listings:
    t1=listing['div'][0]['div'][0]['div'][0]['div'][0]['div'][0]['div'][0]['div'][2]['div'][0]['div']

    for att in t1:
        try:
            print(att['div'][0]['span'][0]['_value'])
        except:
            try:
                print(att['div'][0]['_value'])
            except:
                err.append(att)
                continue
        
for n in [7,6,5,4,3]:
    try:
        driver.find_element_by_xpath("//*[@id='page-top']/div[11]/div/nav/ul/li["+str(n)+"]/button").click()          
        break
    except:
        continue
