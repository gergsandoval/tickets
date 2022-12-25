from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from random import randint
from fake_useragent import UserAgent
from selenium_stealth import stealth
from discord import SyncWebhook
from discord import File
import sys
import requests
import time
import random 
import json
import datetime
import uuid

DISCORD_URL = ""


seetickets = [
    {
        "url": "https://www.seetickets.com/event/pierce-the-veil/manchester-academy/2290887",
        "page": "seetickets", "location": "Manchester", "expected_error": ["Tickets not available"],
        "width": 750, "height": 1250
    },  
]

twickets = [
    {
        "url": "https://www.twickets.live/event/1503498271165784064",
        "page": "twickets", "location": "Manchester", "expected_error": "Sorry, we don't currently have any tickets for this event",
        "width": 750, "height": 1250
    },
]

ticketswap = [
    {
        "url": "https://www.ticketswap.com/event/pierce-the-veil/regular-tickets/52ccbbd8-c669-4555-8385-ba49fc0904c8/2081137",
        "page": "ticketswap", "location": "Manchester", "expected_error": "No tickets available at the moment.",
        "width": 750, "height": 1250
    },
]

def find_tickets(driver, link):
    element_locator = None
    url = link["url"]
    page = link["page"]
    location = link["location"]
    expected_error = link["expected_error"]
    width = link["width"]
    height = link["height"]
    actual_error = None
    result = dict()
    driver.get(url)
    log(url) 
        
    if page == 'seetickets':
        click_xpath(driver, "//button[contains(text(), 'Accept')]")
        element_locator = "//td[@class='note quantity']"
        actual_error = get_list_of_text_xpath(driver, element_locator)
        
    elif page == 'twickets':
        click_xpath(driver, "//div[@class='banner-close']")
        element_locator = "//span[contains(text(), 'Sorry')]"
        actual_error = get_text_xpath(driver, element_locator)
        
    elif page == 'ticketswap':
        click_xpath(driver, "//button[contains(text(), 'Accept')]")
        element_locator = "//*[contains(text(), 'No tickets available at the moment.')]"
        actual_error = get_text_xpath(driver, element_locator)
    
    result["actual"] = actual_error
    result["expected"] = expected_error
    result["are_equal"] = actual_error == expected_error
    #result["are_equal"] = False
    result["screenshot"] = None
    if not result["are_equal"]:
        result["screenshot"] = take_screenshot(driver, page, width, height)
    return result


def click_xpath(driver, xpath):
    try:
        driver.find_element("xpath", xpath).click()
    except:
        pass
    
def get_text_xpath(driver, xpath):
    text = None
    try:
        element = driver.find_element("xpath",xpath)
        return element.text
    except:
        body = get_text_xpath(driver, "//body")
        return ""
    
def get_list_of_text_xpath(driver, xpath):
    text_list = []
    elements = []
    try:
        elements = driver.find_elements("xpath", xpath)
    except: 
        pass
    for element in elements:
        text_list.append(element.text)
    return text_list  
    
def init_driver(timeout):
    ua = UserAgent()
    options = Options()
    options.headless = True
    options.add_argument('log-level=2')
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.implicitly_wait(timeout)
    stealth(driver,
        languages=["en-US", "en"],
        user_agent=ua['google chrome'],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
    return driver 
    
def get_timeout():
    try:
        timeout = sys.argv[1]
    except:
        timeout = 15
    return int(timeout)

def has_internet(timeout):
    url = "https://www.google.com.ar/"
    try:
        request = requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False
        
def teardown(driver):
    driver.quit()

def send_message(link, screenshot = False):
    tag = "<@338182645731033089>  "
    #message = json.dumps(link)
    content = f"{tag}{link}"
    webhook = SyncWebhook.from_url(DISCORD_URL)
    if screenshot is True:
        fp = link["screenshot"]
        file = File(fp = fp)
        webhook.send(content = content, file = file)
    else:
        webhook.send(content)
    
def take_screenshot(driver, prefix, width = 750, height = 1000):
    image_file = str(prefix) + ".png"
    try:
        driver.set_window_size(width, height)
        driver.save_screenshot(image_file)
        return image_file
    except:
        pass
       
def log(text):
    print(str(datetime.datetime.now()) + " => " + str(text))
       
def main():
    try:
        while True:
            timeout = get_timeout()
            if has_internet(timeout):
                driver = init_driver(timeout)
                for link in seetickets + twickets + ticketswap:
                    result = find_tickets(driver, link)
                    link["actual_error"] = result["actual"]
                    if not result["are_equal"]:
                        link["screenshot"] = result["screenshot"]
                        send_message(link, screenshot = True)
                teardown(driver)
                print("---sleeping----")
                time.sleep(300)
            else:
                log("No internet")
                time.sleep(300)
    except Exception as e:
       send_message(e)
       main()

main()