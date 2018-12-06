#!/usr/bin/env python

import mechanize
from bs4 import BeautifulSoup

def use_mechanize():
    br = mechanize.Browser()
    br.set_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0')
    br.set_handle_robots(False)


    r=br.open('https://www.adopteunmec.com') 
    br.select_form(nr=0)
    br['username']='barbarossa_1@autistici.org'
    br['password']='Adottami1'
    r=br.submit() 

    r = br.open('http://www.adopteunmec.com/mySearch')
    br.select_form(nr=1)
    br['age[min]']=20
    br['age[max]']=30
    br['distance[max]']=40
    br['sex']=1 # 0:homme 1:femme
    r=br.submit()

    # Get profiles in html
    html = BeautifoulSoup(r.get_data(), parser='lxml')
    profiles = [p for p in {l.get('href') for l in html.find_all('a')} if isinstance(p, str) and p.find('profile')>0]

    # Get profiles from js...
    # ??

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

def use_selenium():
    br=webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')

    # Login
    br.get('https://www.adopteunmec.com/')
    br.find_element_by_name('username').send_keys('barbarossa_1@autistici.org')
    br.find_element_by_name('password').send_keys('Adottami1')
    br.find_element_by_name('password').submit()
    time.sleep(1)

    # Search
    br.get('https://www.adopteunmec.com/mySearch')
#    br.find_element_by_name('distance[max]').
    br.find_element_by_name('age[min]').submit()
    time.sleep(1)

    # Scroll to end of page
    for i in range(10):
        br.find_element_by_tag_name('html').send_keys(Keys.END)
        time.sleep(.1) # It shouldn't be needed, since it's client code, but maybe send back some data

    # Get page code, and finally scrape all the profiles
    html=BeautifulSoup( br.execute_script("return document.body.innerHTML") )
    profiles=[p for p in {l.get('href') for l in html.find_all('a')} if isinstance(p, str) and p.find('profile')>0]
    print len(profiles)

br=webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')

# Login
br.get('https://www.adopteunmec.com/')
br.find_element_by_name('username').send_keys('justemenemoi@gmail.com')
br.find_element_by_name('password').send_keys('Adottami1')
br.find_element_by_name('password').submit()
time.sleep(1)

# Search
br.get('https://www.adopteunmec.com/mySearch')
# Select distance
ActionChains(aum.br).move_to_element(br.find_element_by_id('by-button')).click().send_keys('distance').send_keys(Keys.ENTER).perform()
#br.find_element_by_name('age[min]').submit()
#time.sleep(1)