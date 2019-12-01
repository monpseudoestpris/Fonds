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
import random

import subprocess as s


NBRPAGES=1

BROWSER="CHROME"




def buildStr(l):
    out=""
    for e in l:
        out +=str(e)+";"
    return(out)

class Main():
    log_level_default = l.INFO

    def __init__(self,file,typeFund):
        self.__TAG = __file__[__file__.rfind(os.sep)+1:]
        self.file=file
        self.typeFund=typeFund
        tag =  self.__TAG + "::" + inspect.stack()[0][3] + ":: "
        time_current = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
        l.debug(tag + "script started at: " + time_current)
        my_dir = os.environ["HOME"] + os.sep + '.' + self.__name()
        session_id = None


        chrome_options = Options()
        headless = True
        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")

        chrome_options.add_argument("--window-size=1920x1080")
        driver = webdriver.Chrome(os.environ['HOME'] + os.sep +
                                  'bin/chromedriver/chromedriver',
                                  chrome_options=chrome_options)

        self.__driver = driver

        command_executor_url = self.__driver.command_executor._url
        #print("browser url =" + command_executor_url)

        self.get_links()




    def get_links(self):
        if self.typeFund == "ETF":
            fileout="ETF.txt"
        if self.typeFund == "Fund":
            fileout = "Fonds.txt"
        f=open(fileout,'w')

        fileIn=self.file
        #print('parsing File:' + fileIn)
        linksIn=[[x.split(";")[0],x.split(";")[1]] for x in open(fileIn,'r').readlines()]
        for fund in linksIn:
            heure = time.localtime().tm_hour
            sys.stderr.write("heure="+str(heure)+"\n")
            while(heure in [21,22,23,0,1,2,3,4,5,6,7]):
                heure = time.localtime().tm_hour
                time.sleep(300)
                sys.stderr.write("Pause !!\n")
            fundName=fund[0]
            fundLink=fund[1]
            #print("on",fundName,fundLink)
            attempt=0

            while(attempt<3):
                try:
                    duration=random.randint(1,3)
                    time.sleep(duration)
                    sys.stderr.write(fundLink)
                    sys.stderr.write("attempt:"+ str(attempt) +"\n")
                    try:
                        self.__driver.get(fundLink)
                        sys.stderr.write("Link read \n")
                    except:
                        pass
                    try:
                        self.__driver.implicitly_wait(10)
                    except:
                        pass
                    try:
                        elementNom = self.__driver.find_element_by_class_name("c-faceplate__company-link")
                        title = elementNom.get_attribute("title").replace("Cours", "")
                        sys.stderr.write("title read \n")
                    except:

                        title="x"
                    try:
                        company = self.__driver.find_element_by_class_name("c-faceplate__price")
                        elementCours = company.find_element_by_class_name("c-instrument")
                        cours = elementCours.text
                        sys.stderr.write("cours read \n")
                    except:

                        cours="x"
                    try:
                        currencyelement = company.find_element_by_class_name("c-faceplate__price-currency")
                        currency = currencyelement.text
                        sys.stderr.write("currency read \n")
                    except:

                        currency="x"
                    try:
                        fundLink=fundLink.replace("\n","")
                    except:
                        pass
                    if self.typeFund == "Fund":
                        try:
                            perfoTable = self.__driver.find_element_by_class_name("c-fund-performances__table")
                            perfos = perfoTable.find_elements_by_class_name("c-table__cell")
                            print("len=",len(perfos))
                            if len(perfos)>6:
                                perfo1janv = perfos[1].text
                                perfo1mois = perfos[2].text
                                perfo6mois = perfos[3].text
                                perfo1an = perfos[4].text
                                perfo3ans = perfos[5].text
                                perfo5ans = perfos[6].text
                                perfo10ans = perfos[7].text
                                sys.stderr.write("perfo read \n")
                            else:
                                perfo1janv = "x"
                                perfo1mois = "x"
                                perfo6mois = "x"
                                perfo1an = "x"
                                perfo3ans = "x"
                                perfo5ans = "x"
                                perfo10ans = "x"
                            sys.stderr.write("perfo done\n")
                        except:

                            perfo1janv = "x"
                            perfo1mois = "x"
                            perfo6mois = "x"
                            perfo1an = "x"
                            perfo3ans = "x"
                            perfo5ans = "x"
                            perfo10ans = "x"
                        try:
                            isin = self.__driver.find_element_by_class_name("c-faceplate__isin").text
                            isincode = isin.split("-")[0]
                            companyname = isin.split("-")[1]
                            sys.stderr.write("isin read \n")
                        except:

                            isin = "x"
                            isincode = "x"
                            companyname = "x"

                        try:
                            cotationElement = self.__driver.find_element_by_class_name("c-faceplate")
                            cotationType = cotationElement.find_element_by_class_name("c-link")
                            cotationType = cotationType.text
                            sys.stderr.write("cotation read\n")
                        except:

                            cotationElement = "x"
                            cotationType = "x"
                        try:
                            strout = buildStr(
                            ["Fonds", title, isincode, companyname, cours, currency, cotationType, perfo1janv,
                             perfo1mois, perfo6mois, perfo1an, perfo3ans, perfo5ans, perfo10ans,fundLink])
                            sys.stderr.write("strout done \n")
                        except:
                            sys.stderr.write("problem with strout\n")
                            attempt = 9999

                    if self.typeFund == "ETF":
                        print("on ETF")
                        try:
                            faceplatedata = self.__driver.find_element_by_class_name("c-faceplate__data")
                            datas = faceplatedata.find_elements_by_class_name("c-instrument")

                            ouverture = datas[0].text
                            haut = datas[1].text
                            bas = datas[3].text
                            volume = datas[4].text
                            ETFtypedata= faceplatedata.find_elements_by_class_name("c-list-info__value")
                            index=8
                            if (ETFtypedata[index].text).find("a")==-1 and (ETFtypedata[index].text).find("e")==-1 and (ETFtypedata[index].text).find("i")==-1 and (ETFtypedata[index].text).find("o")==-1 and (ETFtypedata[index].text).find("u")==-1 and (ETFtypedata[index].text).find("y")==-1:
                                index=9
                            ETFtypedata=ETFtypedata[index].text
                            sys.stderr.write("ETF valeurs  done \n")
                            datas2 = faceplatedata.find_elements_by_class_name("c-list-info__value")
                            indiceRef=datas2[-1].text
                        except:
                            faceplatedata = "x"
                            datas = "x"
                            ouverture = "x"
                            bas = "x"
                            volume = "x"
                            indiceRef="x"

                        try:
                            perfoTable = self.__driver.find_element_by_class_name("c-etf-performances")
                            perfos = perfoTable.find_elements_by_class_name("c-table__cell")
                            if len(perfos) > 6:
                                perfo1janv = perfos[1].text
                                perfo1mois = perfos[2].text
                                perfo3mois = perfos[3].text
                                perfo6mois = perfos[4].text
                                perfo1an = perfos[5].text
                                perfo3ans = perfos[6].text
                                perfo5ans = perfos[7].text
                                perfo10ans = perfos[8].text
                                sys.stderr.write("ETF perfo done \n")
                            else:
                                perfo1mois = "x"
                                perfo3mois = "x"
                                perfo6mois = "x"
                                perfo1an = "x"
                                perfo3ans = "x"
                                perfo5ans = "x"
                                perfo10ans = "x"
                        except:
                            perfo1mois = "x"
                            perfo3mois = "x"
                            perfo6mois = "x"
                            perfo1an = "x"
                            perfo3ans = "x"
                            perfo5ans = "x"
                            perfo10ans = "x"
                            sys.stderr.write("ETF perfo except done \n")
                        try:
                            isin = self.__driver.find_element_by_class_name("c-faceplate__isin").text
                            isincode = isin.split("-")[0]
                            companyname = isin.split("-")[1]
                            sys.stderr.write("ETF isin done \n")
                        except:
                            isin = "x"
                            isincode = "x"
                            companyname = "x"
                            sys.stderr.write("ETF isin except done \n")




                        strout = buildStr(
                            ["ETF", title, isincode, ETFtypedata,companyname, indiceRef,cours, ouverture, haut, bas, volume, currency,
                             perfo1janv, perfo1mois, perfo3mois, perfo6mois, perfo1an, perfo3ans,
                             perfo5ans, perfo10ans,fundLink])

                    f.write(strout+"\n")
                    sys.stderr.write(strout+"\n")
                    attempt=9999
                except:
                    attempt+=1




        f.close()
        self.__driver.close()
        try:
            self.__driver.quit()
            #print("Quited driver")
        except:
            pass

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
    Main(args.file,args.typeFund)

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
    parser.add_argument('-f', '--file', action="store")
    parser.add_argument('-t', '--typeFund', action="store")
    args = parser.parse_args()
    main(args)

