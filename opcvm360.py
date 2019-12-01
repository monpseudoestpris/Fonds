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
import sys
import time

import subprocess as s

class Main():
    log_level_default = l.INFO

    def __init__(self):
        self.__TAG = __file__[__file__.rfind(os.sep)+1:]
        tag =  self.__TAG + "::" + inspect.stack()[0][3] + ":: "
        time_current = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
        l.debug(tag + "script started at: " + time_current)
        my_dir = os.environ["HOME"] + os.sep + '.' + self.__name()
        my_conf_filename ="opcvm360.cfg"
        session_id = None
        print(my_dir + os.sep + my_conf_filename)
        if os.path.exists(my_dir + os.sep + my_conf_filename):
            session_id = open(my_dir + os.sep + 
                              my_conf_filename, 'r').readline()
            print("Existing browser session is available: sessionid ==== "
            + session_id)
        else:
            print("No existing configuration file.")

        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        command_executor = 'http://127.0.0.1:9515'

        self.__driver = webdriver.remote.webdriver.WebDriver(
                    command_executor = command_executor,
                    desired_capabilities = DesiredCapabilities.CHROME,
                    options = chrome_options)
                    #, session_id=session_id)

        command_executor_url = self.__driver.command_executor._url
        print("browser url =" + command_executor_url)

        open(my_dir + os.sep + my_conf_filename, 'w').write(self.__driver.session_id)

        res = ""
        for i in range(1000):
            res += self.get_fund(i+1)

        fo = open('/tmp/out.txt', 'w')
        fo.write(res)

    def get_fund(self, i):
        URL="https://www.opcvm360.com/opcvm/palmares-de-fonds-opcvm360/categoryOpcvm/all/fundType/all/universe/all/sgp/all/currency/EUR/licontract/all/by/perf/page/"+str(i)+"/sortfield/varPYTD/order/DESC"
        print('requesting url:' + URL)
        res = ""
        try:
            self.__driver.get(URL)
        except WebDriverException as e:
            print("Exception while getting the initial URL.")

        self.__driver.implicitly_wait(10)
        print('capturing table')
        try:
            web_element = self.__driver.find_element_by_id('sortable-perf')
            res = web_element.text
        except ElementNotVisibleException:
            print("table not found")
        return res + os.linesep

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
    Main()

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
    args = parser.parse_args()
    main(args)

