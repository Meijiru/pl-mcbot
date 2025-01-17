import asyncio
import time
import os
import logging

from selenium import webdriver
import undetected_chromedriver as uc
from selenium.common.exceptions import ElementNotInteractableException, \
                                       NoSuchElementException, StaleElementReferenceException
                                       
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

#from dotenv import load_dotenv
import re, csv
from random import uniform, randint
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC


#load_dotenv()
USER = "sulfur"
PASSWORD = "Apr72006"
URL = "https://ploudos.com/login/"

# chrome variables
adblock = False  # for those with network wide ad blockers
headless = True  # if you want a headless window

options = webdriver.ChromeOptions()
if headless:
    options.add_argument('--headless')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/87.0.4280.88 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument("start-maximized")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")

driver = uc.Chrome(options=options,executable_path=str(os.environ.get('CHROMEDRIVER_PATH')))


async def start_server():
    """ Starts the server by clicking on the start button.
        The try except part tries to find the confirmation button, and if it
        doesn't, it continues to loop until the confirm button is clicked."""
    element = ""
    while element == "":
        await asyncio.sleep(.5)
        try:
            element = driver.find_element(By.CSS_SELECTOR,'.btn.btn-success')
            element.send_keys(Keys.RETURN)
        except:
            pass

    
    result = True
    
    
    await asyncio.sleep(3)
    # hides the notification question
    #driver.execute_script('hideAlert();')
    # server state span
    while get_status() != "Online":
        await asyncio.sleep(3)
        # while in queue, check for the confirm button and try click it
        
        try:
            if get_status() == "Waiting for confirmation":
                #print("cofirm")
                element = ""
                while element == "":
                    await asyncio.sleep(3)
                    try:
                        element = driver.find_element(By.CSS_SELECTOR,'.btn.btn-success')
                        element.send_keys(Keys.RETURN)
                    except:
                        pass

                return
        except:
            pass
            #driver.execute_script("arguments[0].scrollIntoView();", element)
            #driver.execute_script("arguments[0].queueServer(this,1);", element)

            #element = ""
            #while element == "":
            #    time.sleep(0.5)
            #    element = driver.find_element(By.CSS_SELECTOR,'.btn.btn-success')
            
        

def get_title():
    return driver.title

def get_status():
    """ Returns the status of the server as a string."""
    #print(driver.current_url)
    #print(ms_status)
    
    ms_status = ""
    try:
        ms_status =  driver.find_element(By.XPATH,'//*[@id="status"]/table/tbody/tr[1]/td[2]/span').text
        
        num_tries = 8
        
        while ms_status == "":
            num_tries -= 1

            try:
                ms_status =  driver.find_element(By.XPATH,'//*[@id="status"]/table/tbody/tr[1]/td[2]/span').text
            except:
                pass
            
            if num_tries <= 0:
                break
        

        #print(ms_status)
        if ms_status == "Queue":
            ms_status = "Queued"
    except:
        pass
            
    return ms_status

    #driver.find_element(By.XPATH,'//div[@class="body"]/main/section/div[@class="page-content page-server"]').text

def get_queue():
    """ Returns the status of the server as a string."""
    try:
        ms_status =  driver.find_element(By.XPATH,'//*[@id="status"]/table/tbody/tr[3]/td[2]/span').text
        #print(f"{ms_status} yo over here")
        
        return ms_status
    except:
        pass

def get_number_of_players():
    
    status = get_status()
    """ Returns the number of players as a string.
        Works: When server is online--Returns 0 if offline"""
    if status == "Online":
        return driver.find_element(By.CSS_SELECTOR,'.live-status-box-value.js-players').text
        #return driver.find_element(By.XPATH,'//*[@id="nope"]/main/section'
        #                                    '/div[3]/div[5]/div[2]/div['
        #                                    '1]/div[1]/div[2]/div[2]').text
    else:
        # Can't be 0/20 because max isn't always the same,
        # could maybe pull max players from options page
        return '0'


def get_ip():
    """ Returns the severs IP address.
        Works: Always works"""
    return "sulfursurf.ploudos.me" #driver.find_element(By.XPATH,'//span[@id="ip"]').text


def get_software():
    """ Returns the server software.
        Works: Always works"""
    return driver.find_element(By.XPATH,'//*[@id="software"]').text


def get_version():
    """ Returns the server version.
        Works: Always works"""
    if get_status() == "Online":
        return driver.find_element(By.XPATH,'//*[@id="status"]/table/tbody/tr[4]/td[2]/span').text
    else:
        return driver.find_element(By.XPATH,'//*[@id="status"]/table/tbody/tr[2]/td[2]/span').text

def get_tps():
    """ Returns the server TPS
        Works; When the server is online--Returns '0' if offline"""
    try:
        return driver.find_element(By.CSS_SELECTOR,'."live-status-box-value.js-tps"').text
    except NoSuchElementException:
        return '0'


def get_server_info():
    """ Returns a string of information about the server
        Returns: server_ip, server_status, number of players, software,
        version"""
        
    server_status = get_status()
    position = ""

    if server_status == "Queued":
        position = get_queue()
        server_status = f"Queued {position}"
    
    return get_ip(), server_status, \
           get_version()



#def connect_account():
#    time.sleep(5)
#    print(driver.title)
#    if driver.title != "Attention Required! | Cloudflare":
#        connect()
#    else:
#        recaptcha_process()
#        time.sleep(70)
#        #waitUntil(driver.title != "Attention Required! | Cloudflare", connect())

async def connect_account():
    driver.get(URL)
    """ Connects to the accounts through a headless chrome tab so we don't
        have to do it every time we want to start or stop the server."""
    # login to PloudOS
    print(driver.title)

        
    element = driver.find_element(By.XPATH,'//*[@name="username"]')
    element.send_keys(USER)
    element = driver.find_element(By.XPATH,'//*[@name="password"]')
    element.send_keys(PASSWORD)
    element = driver.find_element(By.XPATH,'//*[@class="btn btn-primary"]')
    element.send_keys(Keys.RETURN)
    
    while driver.current_url != "https://ploudos.com/server/":
        await asyncio.sleep(5)
        # print(driver.current_url)
    
    alert = ""
    try:
        alert = driver.find_element(By.CSS_SELECTOR,'.alert.alert-warning').text
    except:
        pass
    
    while alert != "":
        driver.refresh()
        await asyncio.sleep(5)
        try:
            alert = driver.find_element(By.CSS_SELECTOR,'.alert.alert-warning').text
        except:
            pass
    
    
    element_text = ""
    element = ""
    while element_text != "Manage":
        await asyncio.sleep(2)
        try:
            element = driver.find_element(By.CSS_SELECTOR,'.btn.btn-success.btn-xs')
            element_text = element.text
        except:
            pass

        print(element_text)
        print(driver.title)
        print("----------")
        print("")
    # selects server from server list
    
    trying = True
    stage2 = False
    while trying == True:
        await asyncio.sleep(2)
        trying = False
        try:
            element.send_keys(Keys.RETURN)
        except:
            trying = True
            try:
                if stage2 == False:

                    agree_button = driver.find_element(By.XPATH,'//*[@class=" css-47sehv"]')
                    agree_button.send_keys(Keys.RETURN)
                    stage2 = True
                elif stage2 == True:
                    save_button = driver.find_element(By.XPATH,'//*[contains(text(), "SAVE & EXIT")]')
                    save_button.send_keys(Keys.RETURN)
            except:
                pass
    

        
    
    while driver.title != "PloudOS.com - Manage server":
        await asyncio.sleep(5)
        #print(driver.title)

    time.sleep(12)
    print(driver.title)
    
    
    #driver.find_element(By.XPATH,"/html/body/")
    # by passes the 3 second adblock
    if adblock:
        adblockBypass()

    logging.info('PloudOS Tab Loaded')




def adblockBypass():
    time.sleep(1)   
    element = driver.find_element(By.XPATH,'//*[@id="sXMbkZHTzeemhBrPtXgBD'
                                           'DwAboVOOFxHiMjcTsUwoIOJ"]/div/'
                                           'div/div[3]/div[2]/div[3]/div'
                                           '[1]')
    element.click()
    time.sleep(3)
    logging.debug("Adblock Wall Bypassed")


async def stop_server():
    """ Stops server from PloudOS panel."""
    element = driver.find_element(By.XPATH,"//*[@id=\"stop\"]")
    element.click()


def quitBrowser():
    """ Quits the browser driver cleanly."""
    driver.quit()


def refreshBrowser():
    driver.refresh()