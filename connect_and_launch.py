import asyncio
from time import time
import os
import logging
import undetected_chromedriver as uc

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, \
                                       NoSuchElementException
from dotenv import load_dotenv
import re, csv
from random import uniform, randint
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC


load_dotenv()
USER = "NyceTurtle"
PASSWORD = "Apr72006"
URL = "https://aternos.org/go/"

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
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")

driver = uc.Chrome(options=options,executable_path=os.environ.get("CHROMEDRIVER_PATH"))

def waitUntil(condition, output): #defines function
    wU = True
    while wU == True:
        if condition: #checks the condition
            output
            wU = False
        time.sleep(60) #waits 60s for preformance

async def start_server():
    """ Starts the server by clicking on the start button.
        The try except part tries to find the confirmation button, and if it
        doesn't, it continues to loop until the confirm button is clicked."""
    element = driver.find_element_by_xpath("//*[@id=\"start\"]")
    element.click()
    await asyncio.sleep(3)
    # hides the notification question
    driver.execute_script('hideAlert();')
    # server state span
    while get_status() == "Waiting in queue":
        # while in queue, check for the confirm button and try click it
        await asyncio.sleep(3)
        try:
            element = driver.find_element_by_xpath('//*[@id="confirm"]')
            element.click()
        except ElementNotInteractableException:
            pass


def get_status():
    """ Returns the status of the server as a string."""
    return driver.find_element_by_css_selector('.statuslabel-label').text
    #driver.find_element_by_xpath('//div[@class="body"]/main/section/div[@class="page-content page-server"]').text


def get_number_of_players():
    
    status = driver.find_element_by_css_selector('.statuslabel-label').text
    """ Returns the number of players as a string.
        Works: When server is online--Returns 0 if offline"""
    if status == "Online":
        return driver.find_element_by_css_selector('.live-status-box-value.js-players').text
        #return driver.find_element_by_xpath('//*[@id="nope"]/main/section'
        #                                    '/div[3]/div[5]/div[2]/div['
        #                                    '1]/div[1]/div[2]/div[2]').text
    else:
        # Can't be 0/20 because max isn't always the same,
        # could maybe pull max players from options page
        return '0'


def get_ip():
    """ Returns the severs IP address.
        Works: Always works"""
    return driver.find_element_by_xpath('//span[@id="ip"]').text


def get_software():
    """ Returns the server software.
        Works: Always works"""
    return driver.find_element_by_xpath('//*[@id="software"]').text


def get_version():
    """ Returns the server version.
        Works: Always works"""
    return driver.find_element_by_xpath('//*[@id="version"]').text


def get_tps():
    """ Returns the server TPS
        Works; When the server is online--Returns '0' if offline"""
    try:
        return driver.find_element_by_css_selector('."live-status-box-value.js-tps"').text
    except NoSuchElementException:
        return '0'


def get_server_info():
    """ Returns a string of information about the server
        Returns: server_ip, server_status, number of players, software,
        version"""
    return get_ip(), get_status(), get_number_of_players(), \
           get_software(), get_version(), get_tps()

def waitUntil(condition, output): #defines function
    wU = True
    while wU == True:
        if condition: #checks the condition
            output
            wU = False
        time.sleep(60) #waits 60s for preformance

def connect_account():
    if driver.title == "Attention Required! | Cloudflare":
        recaptcha_process(driver)
        waitUntil(driver.title != "Attention Required! | Cloudflare", connect())
    else:
        connect()

def connect():
    """ Connects to the accounts through a headless chrome tab so we don't
        have to do it every time we want to start or stop the server."""
    # login to aternos
    
    driver.get(URL)
    print(driver.title)

    while driver.title != "Login or Sign up | Aternos | Free Minecraft Server":
        time.sleep(5)
        print(driver.title) 
        driver.refresh()
        
    element = driver.find_element_by_xpath('//*[@id="user"]')
    element.send_keys(USER)
    element = driver.find_element_by_xpath('//*[@id="password"]')
    element.send_keys(PASSWORD)
    element = driver.find_element_by_xpath('//*[@id="login"]')
    element.click()
    while driver.title != "Servers | Aternos | Free Minecraft Server" :
        time.sleep(5)
        print(driver.title)
        driver.refresh()

    # selects server from server list
    element = driver.find_element_by_css_selector('.server-body')
    element.click()
    
    time.sleep(2)
    
    while driver.title != "Server | Aternos | Free Minecraft Server" :
        time.sleep(5)
        print(driver.title)
        driver.refresh()
    
    #driver.find_element_by_xpath("/html/body/")
    # by passes the 3 second adblock
    if adblock:
        adblockBypass()

    logging.info('Aternos Tab Loaded')


def adblockBypass():
    time.sleep(1)
    element = driver.find_element_by_xpath('//*[@id="sXMbkZHTzeemhBrPtXgBD'
                                           'DwAboVOOFxHiMjcTsUwoIOJ"]/div/'
                                           'div/div[3]/div[2]/div[3]/div'
                                           '[1]')
    element.click()
    time.sleep(3)
    logging.debug("Adblock Wall Bypassed")


async def stop_server():
    """ Stops server from aternos panel."""
    element = driver.find_element_by_xpath("//*[@id=\"stop\"]")
    element.click()


def quitBrowser():
    """ Quits the browser driver cleanly."""
    driver.quit()


def refreshBrowser():
    driver.refresh()


def write_stat(loops, time):
    with open('stat.csv', 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow([loops, time])


def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def wait_between(a, b):
    rand = uniform(a, b)
    time.sleep(rand)

def dimention(driver):
    d = int(driver.find_element_by_xpath('//div[@id="rc-imageselect-target"]/table').get_attribute("class")[-1]);
    return d if d else 3  # dimention is 3 by default


# ***** main procedure to identify and submit picture solution
def solve_images(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "rc-imageselect-target"))
    )
    dim = dimention(driver)
    # ****************** check if there is a clicked tile ******************
    if check_exists_by_xpath(
            '//div[@id="rc-imageselect-target"]/table/tbody/tr/td[@class="rc-imageselect-tileselected"]'):
        rand2 = 0
    else:
        rand2 = 1

    # wait before click on tiles
    wait_between(0.5, 1.0)
    # ****************** click on a tile ******************
    tile1 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(
            randint(1, dim), randint(1, dim))))
    )
    tile1.click()
    if (rand2):
        try:
            driver.find_element_by_xpath(
                '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(randint(1, dim),
                                                                                        randint(1, dim))).click()
        except NoSuchElementException:
            print('\n\r No Such Element Exception for finding 2nd tile')

    # ****************** click on submit buttion ******************
    driver.find_element_by_id("recaptcha-verify-button").click()

def recaptcha_process(driver):
    try:
        # move the driver to the first iFrame
        # driver.switch_to_frame(driver.find_elements_by_tag_name("iframe")[0])
        driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[0])

        # *************  locate CheckBox  **************
        CheckBox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "recaptcha-anchor"))
            # EC.presence_of_element_located((By.CLASS_NAME, "recaptcha-checkbox-borderAnimation"))
        )

        # *************  click CheckBox  ***************
        # making click on captcha CheckBox
        CheckBox.click()

        # ***************** back to main window **************************************
        # driver.switch_to_window(mainWin)
        driver.switch_to.window(mainWin)

        wait_between(2.0, 2.5)

        # ************ switch to the second iframe by tag name ******************
        # driver.switch_to_frame(driver.find_elements_by_tag_name("iframe")[1])
        driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[1])
        i = 1
        while i < 300:
            print('\n\r{0}-th loop'.format(i))
            # ******** check if checkbox is checked at the 1st frame ***********
            # driver.switch_to_window(mainWin)
            driver.switch_to.window(mainWin)
            WebDriverWait(driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, 'iframe'))
            )
            wait_between(1.0, 2.0)
            if check_exists_by_xpath('//span[@aria-checked="true"]'):
                import winsound

                winsound.Beep(400, 1500)
                write_stat(i, round(time() - start) - 1)  # saving results into stat file
                break

            # driver.switch_to_window(mainWin)
            driver.switch_to.window(mainWin)
            # ********** To the second frame to solve pictures *************
            wait_between(0.3, 1.5)
            # driver.switch_to_frame(driver.find_elements_by_tag_name("iframe")[1])
            driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[1])
            solve_images(driver)
            i = i + 1
    except:
        pass
    return driver
