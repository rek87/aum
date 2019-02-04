#!/usr/bin/env python

from requestium import Session, Keys
from bs4 import BeautifulSoup
import time
import datetime
import shutil
import json

class Charme(object):
    def __init__(self):
        # Create a session and authenticate
        self._s = Session(webdriver_path='/usr/lib/chromium-browser/chromedriver', browser='chrome') #,
            #webdriver_options={"arguments": ["--headless"]})
        self._s.headers.update(
            {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'})

        # Login
        r = self._s.post('https://www.adopteunmec.com/auth/login',
            data={'username':'bbrss@autistici.org', 'password':'Adottami1'})
        if not r.ok:
            raise 'Something wrong in login'
        else:
            time.sleep(2)


    def search_by_distance(self, age_min=20, age_max=30, distance=40, sex=1):
        return self.search(
            {'age[min]':age_min, 'age[max]':age_max, 'by':'distance', 'distance[max]':distance, "sex":sex})

    def search(self, criteria=None):
        if criteria is None:
            return []

        # Go to search page
        self._s.get('https://www.adopteunmec.com/mySearch')
        time.sleep(1)
        # POST a request
        r = self._s.post('https://www.adopteunmec.com/mySearch/save', data=criteria)

        time.sleep(3) # Wait a bit...
        # Trasnfer cookie to selenium, refresh the page, scroll to end 10 times, and get profiles
        self._s.transfer_session_cookies_to_driver()
        self._s.driver.get('https://www.adopteunmec.com/mySearch/results')
        for i in range(10):
            self._s.driver.find_element_by_tag_name('html').send_keys(Keys.END)
            time.sleep(.1)
        html=BeautifulSoup(
            self._s.driver.execute_script("return document.body.innerHTML"), 'lxml')
        self._s.transfer_driver_cookies_to_session()
        self._s.driver.close() # Might be done before ?

        # Look for <div> tags containing user info
        blocks = html.find_all('div', {'class':'user-infos'})
        # Get all <a> tags in a same list
        all_a = [a for sl in [b.find_all('a') for b in blocks] for a in sl]
        # Extract profiles ID doing common name checks to avoid visit too may profiles later
        profiles = [l.get('href').split('/')[-1]
            for l in all_a if isinstance(l.get('href'), str)
                and l.get('href').find('profile') > 0
                and len(l.get_text()) > 2]
        return profiles

    def charme(self, profiles=[], max_p=10, filename='data/charme.json'):
        db = {}
        try:
            with open(filename, 'r') as in_f:
                db = json.load(in_f)
        except:
            pass

        visited = 0
        for uid in profiles:
            # Check if profile already in db
            if uid not in db:
                if max_p is not None and visited >= max_p:
                    break
                visited += 1

                url = "https://www.adopteunmec.com/profile/" + uid
                print "Visiting", url
                page = self._s.get(url)
                html = BeautifulSoup(page.content.decode('utf-8', 'xmlcharrefreplace'), 'lxml')

                img_url = html.find(id='img-current-pic')['src']
                img_name = img_url.split('/')[-1]
                date = datetime.datetime.now().strftime("%m-%d %H:%M")
                db[uid] = {
                    "profile": url,
                    "name": html.find('div', {'class':'username'}).get_text(),
                    "img": img_name,
                    "age": html.find('span', {'class':'age'}).get_text(),
                    "city": html.find('span', {'class':'city'}).get_text(),
                    "desc": html.find(text='Description').find_parent('div').find('p').get_text(),
                    "shop": html.find(text='Shopping List').find_parent('div').find('p').get_text(),
                    "charmed": date
                    }

                # Download and save profile pic
                pic = self._s.get(img_url, stream=True)
                pic.raw.decode_content=True
                with open("data/pics/" + img_name, 'wb') as f:
                    shutil.copyfileobj(pic.raw, f)

                time.sleep(20) # Bit of rest...

                # Send a charme
                url = "https://www.adopteunmec.com/events/charm?id=" + uid
                r = self._s.get(url)
                if r.json()['member']['id'] != uid:
                    raise 'Something wrong in response'


        # Write back json
        json_s = json.dumps(db) # Dump as a string, to write to file and as JS var
        with open(filename, 'w') as out_f:
            out_f.write(json_s)
