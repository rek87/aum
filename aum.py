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

from requestium import Session, Keys
import json
import shutil
from random import randint

# Seems to work
def trial3(filename='data/justemenemoi.json'):  
    # Use requests to authenticate and do search
    s=Session(webdriver_path='/usr/lib/chromium-browser/chromedriver', browser='chrome')
    s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'})
    r=s.get('https://www.adopteunmec.com')
    r=s.post('https://www.adopteunmec.com/auth/login', data={'username':'justemenemoi@gmail.com', 'password':'Adottami1'})
    r=s.get('https://www.adopteunmec.com/mySearch')

    r=s.post('https://www.adopteunmec.com/mySearch/save', data={'age[min]':25, 'age[max]':26, 'by':'distance', 'distance[max]':10})
    html = BeautifulSoup(r.text, 'lxml')
    profiles = [p for p in {l.get('href') for l in html.find_all('a')} if isinstance(p, str) and p.find('profile')>0]
    print len(profiles)

    time.sleep(3)
    
    # Trasnfer cookie to selenium, refresh the page, scroll to end 10 times, and get profiles
    s.transfer_session_cookies_to_driver()
    s.driver.get('https://www.adopteunmec.com/mySearch/results')
    for i in range(10):
        s.driver.find_element_by_tag_name('html').send_keys(Keys.END)
        time.sleep(.1)
    html=BeautifulSoup( s.driver.execute_script("return document.body.innerHTML") )
    profiles = [p for p in {l.get('href') for l in html.find_all('a')} if isinstance(p, str) and p.find('profile')>0]
    print len(profiles)

    # Load already visited profiles
    db = {}
    try:
        with open(filename, 'r') as in_f:
            db = json.load(in_f)
    except:
        pass

    # Loop on profiles, get descriptions
    s.transfer_driver_cookies_to_session()
    s.driver.close() # Might be done before ?
    profiles=[profiles[randint(0, len(profiles))]]
    for p in profiles:
        # Check if profile already in db
        uid = p.split('/')[-1]
        if uid not in db:
            page = s.get(p)
            html = BeautifulSoup(page.text)
            
            img_url = html.find(id='img-current-pic')['src']
            img_name = img_url.split('/')[-1]
            db[uid] = {
                "name": html.find('div', {'class':'username'}).get_text(),
                "img": img_name,
                "age": html.find('span', {'class':'age'}).get_text(),
                "city": html.find('span', {'class':'city'}).get_text(),
                "desc": html.find(text='Description').find_parent('div').find('p').get_text(),
                "shop": html.find(text='Shopping List').find_parent('div').find('p').get_text() }
            
            # Download and save profile pic
            pic=s.get(img_url, stream=True)
            pic.raw.decode_content=True
            with open("data/" + img_name, 'wb') as f:
                shutil.copyfileobj(pic.raw, f)

    # Write back json
    json_s = json.dumps(db) # Dump as a string, to write to file and as JS var
    with open(filename, 'w') as out_f:
        out_f.write(json_s)
    with open(filename + '.js', 'w') as out_f:
        out_f.write("data = ")
        out_f.write(json_s)
    

# Tinder
# x-auth-token	c7ff6484-8fbd-4246-94f0-71b813957c0e
#https://www.facebook.com/fede.rek.7
#https://www.facebook.com/photo.php?fbid=897484456993922&set=a.101328586609517&type=3&source=11&referrer_profile_id=100001971275275
# ID:
#https://www.facebook.com/100001971275275