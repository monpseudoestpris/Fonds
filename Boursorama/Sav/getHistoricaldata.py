#!/usr/bin/env python3

# Pre-requesites:
#   sudo pip3 install selenium
#   sudo apt-get install phantomjs

import argparse
import datetime
import inspect
import json
import logging as l
import re
import os
import selenium
from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.command import Command
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import sys
import time
import psutil
import glob


import subprocess as s


NBRPAGES=1

BROWSER="CHROME"


def enable_download_in_headless_chrome(browser, download_dir):
    #add missing support for chrome "send_command"  to selenium webdriver
    browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    browser.execute("send_command", params)

def buildStr(l):
    out=""
    for e in l:
        out +=str(e)+";"
    return(out)

class Main():
    log_level_default = l.INFO

    def __init__(self,url,all):
        self.__TAG = __file__[__file__.rfind(os.sep)+1:]
        self.url=url
        self.all=all
        tag =  self.__TAG + "::" + inspect.stack()[0][3] + ":: "
        time_current = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
        l.debug(tag + "script started at: " + time_current)
        my_dir = os.environ["HOME"] + os.sep + '.' + self.__name()
        session_id = None


        if BROWSER=="CHROME":
            chrome_options = Options()
            headless = True
            if headless:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-gpu")

            chrome_options.add_argument("--window-size=1920x1080")
            driver = webdriver.Chrome(os.environ['HOME'] + os.sep +
                                      'bin/chromedriver/chromedriver',
                                      chrome_options=chrome_options)



            #chrome_options.add_argument("--headless")

            self.__driver = driver
                        #, session_id=session_id)

            if headless:
                enable_download_in_headless_chrome(self.__driver, "/home/chabert/Téléchargements/")
        if BROWSER=="FIREFOX":
            options = webdriver.FirefoxOptions()
            options.add_argument('-headless')
            options.add_argument("--window-size=1920x1080")
            driver = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver", firefox_options=options)
            self.__driver = driver

        command_executor_url = self.__driver.command_executor._url
        print("browser url =" + command_executor_url)



        strout=self.get_links()
        print(strout)
        self.getData()




    def getData(self):
        lfiles=glob.glob("./DataFunds/tmp/*txt")


    def get_links(self):
        os.system("rm /home/chabert/Téléchargements/*.txt")
        os.system("rm ./DataFunds/tmp/*.txt")
        URL=self.url
        getHisto=self.all
        print('requesting url:' + URL)
        res = ""
        try:
            self.__driver.get(URL)
        except WebDriverException as e:
            print("Exception while getting the initial URL.")

        self.__driver.implicitly_wait(10)
        elementNom = self.__driver.find_element_by_class_name("c-faceplate__company-link")
        title = elementNom.get_attribute("title").replace(" ","").replace("Cours","")
        company=self.__driver.find_element_by_class_name("c-faceplate__price")
        elementCours=  company.find_element_by_class_name("c-instrument")
        cours=elementCours.text
        currencyelement=company.find_element_by_class_name("c-faceplate__price-currency")
        currency=currencyelement.text


        try:
            perfoTable=  self.__driver.find_element_by_class_name("c-fund-performances__table")
            perfos=perfoTable.find_elements_by_class_name("c-table__cell")
            isin=self.__driver.find_element_by_class_name("c-faceplate__isin").text

            perfo1janv=perfos[1].text
            perfo1mois=perfos[2].text
            perfo6mois = perfos[3].text
            perfo1an = perfos[4].text
            perfo3ans = perfos[5].text
            perfo5ans = perfos[6].text
            perfo10ans = perfos[7].text
            cotationElement = self.__driver.find_element_by_class_name("c-faceplate")
            cotationType = cotationElement.find_element_by_class_name("c-link")
            cotationType = cotationType.text
            strout=buildStr(["Fonds",title,isin,cours,currency,cotationType,perfo1janv,perfo1mois,perfo6mois,perfo1an,perfo3ans,perfo5ans,perfo5ans,perfo10ans])
        except Exception as e:
            print("Exception",e)

            faceplatedata=self.__driver.find_element_by_class_name("c-faceplate__data")
            datas=faceplatedata.find_elements_by_class_name("c-instrument")

            ouverture=datas[0].text
            haut=datas[1].text
            bas=datas[3].text
            volume=datas[4].text
            perfoTable = self.__driver.find_element_by_class_name("c-etf-performances")
            perfos = perfoTable.find_elements_by_class_name("c-table__cell")
            isin=self.__driver.find_element_by_class_name("c-faceplate__isin").text



            perfo1janv = perfos[1].text
            perfo1mois = perfos[2].text
            perfo3mois = perfos[3].text
            perfo6mois = perfos[4].text
            perfo1an = perfos[5].text
            perfo3ans = perfos[6].text
            perfo5ans = perfos[7].text
            perfo10ans = perfos[8].text

            strout = buildStr(["ETF",title, isin,cours,ouverture,haut,bas,volume, currency, perfo1janv, perfo1mois,perfo3mois, perfo6mois, perfo1an, perfo3ans,
                 perfo5ans, perfo5ans, perfo10ans])

        if getHisto=="True":
            try:
                print("Downloading data")

                years = self.__driver.find_elements_by_class_name("c-quote-chart__length")
                for y in years:
                    action = ActionChains(self.__driver)
                    action.move_to_element(y).perform()
                    y.click()
                    time.sleep(5)
                    web_element = self.__driver.find_elements_by_class_name("c-quote-chart__menu-button-icon")
                    action = ActionChains(self.__driver)
                    action.move_to_element(web_element[2]).perform()
                    web_element[2].click()
                    time.sleep(2)


                os.system("cp /home/chabert/Téléchargements/*.txt ./DataFunds/tmp/")



            except ElementNotVisibleException:
                print("table not found")
        self.__driver.close()
        try:
            self.__driver.quit()
            print("Quited driver")
        except:
            pass
        return(strout)

    def __name(self):
        pos = __file__.rfind(os.sep)+1
        name_with_py_ext = __file__[pos:]
        name = re.sub('\.py$', '', name_with_py_ext)
        assert name !=  name_with_py_ext, "can't find python .py extension"

        return name



def log_path():
    script_filename = os.path.abspath(__file__)
    pos = script_filename.rfind(os.sep) + 1
    script_filename = script_filename[pos:]
    base_path = re.sub('\.py$', '', script_filename)
    assert base_path != script_filename, "can't find python .py extension"
    base_path = '.' + base_path
    base_path = os.environ['HOME'] + os.sep + base_path
    os.makedirs(base_path, exist_ok=True)
    return base_path + os.sep + 'log.txt'

def main(args):
    my_log_path = log_path()
    l.basicConfig(filename=my_log_path,
                  format='%(asctime)s %(message)s', level=args.log_level)
    if not args.silent_log:
        hdlr = l.StreamHandler(sys.stdout)
        l.root.addHandler(hdlr)
    l.debug("logs will be stored into " + my_log_path)
    Main(args.url,args.all)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="script description")
    parser.add_argument('-l', '--log_level', default=Main.log_level_default,
                        help="set the log level. Possible values: " +
                        ' '.join(list(l._nameToLevel.keys())) + ". Default: " +
                        l._levelToName[Main.log_level_default])
    parser.add_argument('-s', '--silent_log', action="store_true",
                        help="don't output log to stdout, only log it into: " +
                        log_path() +
                        ". Default is to log to both")
    parser.add_argument('-u', '--url', action="store")
    parser.add_argument('-a', '--all', action="store")
    args = parser.parse_args()
    main(args)

