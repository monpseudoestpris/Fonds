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


os.system("python3 getLinksFunds.py")
os.system("python3 classeFonds.py -f linksFunds.txt -t Fund > Perfos/Fonds.txt")



