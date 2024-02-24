from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import threading
from selenium.webdriver.common.by import By
#from bs4 import BeautifulSoup
import csv
import time
import re
import json


def create_webdriver(url):
    opt = Options()
    opt.add_argument("--headless")
    
    driver = webdriver.Edge(options=opt)
    driver.get(url)
    driver.maximize_window()
    
    return driver



def get_version_product(driver, url):
    version_dict = {}
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.box03.group.desk:not([class*='color'])")))
        box_version = driver.find_element(By.CSS_SELECTOR, "div.box03.group.desk:not([class*='color'])").find_elements(By.TAG_NAME, "a")
    except:
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "box03.color.group.desk")))
            box_version = driver.find_element(By.CLASS_NAME, "box03.color.group.desk").find_elements(By.TAG_NAME, "a")
        except:
            print(f"Doesn't have informations of version from {url}")
            return None
    
    for version_index in range(len(box_version)):
        version_found = True
        
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "box03.group.desk")))
            version = driver.find_element(By.CSS_SELECTOR, "div.box03.group.desk:not([class*='color'])").find_elements(By.TAG_NAME, "a")[version_index]
        except:
            print(f"Doesn't have version of item from {url}")
            version_name = None
            version_found = False
            
        if version_found:
            try:
                version_name = version.text
                version_url = version.get_attribute('href')
                version.click()
            except:
                print(f"Can't get version of item from {url}")
                version_name = None
      
        try:
            box_color = driver.find_element(By.CLASS_NAME, "box03.color.group.desk").find_elements(By.TAG_NAME, "a")
        
            for i in range(len(box_color)):
                
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "box03.color.group.desk")))
                try:
                    color = driver.find_element(By.CLASS_NAME, "box03.color.group.desk").find_elements(By.TAG_NAME, "a")[i]
                    color_name = color.text
                    url_color = color.get_attribute('href')
                # print(color_name
                    color.click()
                except:
                    print(f"Can't get color_url, color_name / doesn't have color of item from {url}")
                    color_name = None
                    
                
                try:
                # prices = driver.find_element(By.CLASS_NAME, "box-price")
                    price = driver.find_element(By.CLASS_NAME, 'box-price-old').get_attribute('textContent')
                except:
                    try:
                        price = driver.find_element(By.CLASS_NAME, 'box-price-present').get_attribute('textContent')
                    except:
                        print(f"Can't get price of item from {url}")
                
                if (version_name is None and color_name is None):
                    continue
                elif (version_name is None):
                    key_dict = color_name
                elif (color_name is None):
                    key_dict = version_name
                else:
                    key_dict = version_name + '_' + color_name
                    
                                    
                item_dict = {
                    'url': url_color if url_color is not None else version_url,
                    'giá': price
                }
                
                
                version_dict[key_dict] = item_dict
        except:
            try:
                price = driver.find_element(By.CLASS_NAME, 'box-price-old').get_attribute('textContent')
            except:
                try:
                    price = driver.find_element(By.CLASS_NAME, 'box-price-present').get_attribute('textContent')
                except:
                    print(f"Can't get price of item from {url}")
                    
            item_dict = {
                    'url': version_url,
                    'giá': price
            }
            
            version_dict[version_name] = item_dict
            
            time.sleep(2)
        time.sleep(2)
    
    return version_dict



def get_data(driver, url, category_name):
    
    ## Get name of item
    try:
        name = driver.find_element(By.TAG_NAME, 'h1').text
    except:
        print(f"Can't get name of item from {url}")
        return 0
    
    # Get price of item
    try:
        # prices = driver.find_element(By.CLASS_NAME, "box-price")
        price = driver.find_element(By.CLASS_NAME, 'box-price-old').get_attribute('textContent')
    except:
        try:
            price = driver.find_element(By.CLASS_NAME, 'box-price-present').get_attribute('textContent')
        except:
            print(f"Can't get price of item from {url}")
            return 0
    
    # Get features of item
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "btn-detail.btn-short-spec")))
        button_detail = driver.find_element(By.CLASS_NAME, 'btn-detail.btn-short-spec')
        button_detail.click()
        print("Scraping...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "parameter-item")))
        features = driver.find_elements(By.CLASS_NAME, 'parameter-item')
        feature_dict = {}
        if len(features) != 1:
            for feature in features:
                elements = feature.find_elements(By.TAG_NAME, 'li')
                name_feature = feature.find_element(By.CLASS_NAME, 'parameter-ttl').text
                detail = {}
                for element in elements:
                    left = element.find_element(By.CSS_SELECTOR, ".ctLeft")
                    right = element.find_element(By.CSS_SELECTOR,".ctRight")
                    key = left.text.strip(":")
                    value = right.text
                    detail[key] = value
                feature_dict[name_feature] = detail
        else:
            list_features = driver.find_element(By.CLASS_NAME, "ulist").find_elements(By.TAG_NAME, "li")
            detail = {}
            for feature in list_features:
                left = feature.find_element(By.CSS_SELECTOR, ".ctLeft")
                right = feature.find_element(By.CSS_SELECTOR,".ctRight")
                key = left.text.strip(":")
                value = right.text
                detail[key] = value
            
        time.sleep(3)
        driver.find_element(By.CLASS_NAME, 'btn-closemenu.close-tab').click()
        # print(feature_dict)
    except:
        try:
            feature_dict = {}
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "parameter")))
            list_features = driver.find_element(By.CLASS_NAME, "parameter").find_elements(By.TAG_NAME, "li")
            detail = {}
            for feature in list_features:
                left = feature.find_element(By.CLASS_NAME, "lileft")
                right = feature.find_element(By.CLASS_NAME,"liright")
                key = left.text
                value = right.text
                detail[key] = value
        except:
            print(f"Can't get features of item from {url}")
            return 0
    
    # Get versions of item
    version_dict = get_version_product(driver, url)
       
    # Save into dict item
    item = {
    "tên_sản_phẩm": name,
    "url": url,
    "loại": category_name,
    "giá_tiền_gốc": price,
    "tính_năng": feature_dict if bool(feature_dict) else detail,
    "phiên_bản": version_dict
    }
    
    return item



def scrape_data(file):
    

    url_item = []
    with open(file, "r") as f:
        for line in f:
            url_item.append(line.strip())
    
    list_item = []
    list_error_item = []
    
    i = 0
    max_item = len(url_item)
    
    for url in url_item:
        print(f"Starting item {i} / {max_item}", end="->")
        driver = create_webdriver(url)
        category = re.search(r"https:\/\/www\.thegioididong\.com\/([^\/]+)", url).group(1)
        item = get_data(driver, url, category)
        
        if item == 0:
            list_error_item.append(url)
            driver.close()
            continue
        else:
            list_item.append(item)
            print(f"Done item {i} / {max_item}")
            driver.close()
        
        i +=1
        time.sleep(3)

    return list_item, list_error_item