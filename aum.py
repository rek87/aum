#!/usr/bin/env python

from requestium import Session, Keys
import json
import shutil
from random import randint
from bs4 import BeautifulSoup
import time

class AuM(object):
    def __init__(self):
        # Create a session and authenticate
        self._s = Session(webdriver_path='/usr/lib/chromium-browser/chromedriver', browser='chrome')
        self._s.headers.update(
            {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'})
        self._s.get('https://www.adopteunmec.com')
        # TODO: check successful login
        self._s.post('https://www.adopteunmec.com/auth/login',
            data={'username':'meredithabt@gmail.com', 'password':'Adottami9'})

        self._common_names=('m', 'loic', 'marc', 'anthony', 'tom', 'jordan', 'florian', 'jean', 'manu', 'seb',
            'alex', 'lilian', 'angelo', 'fred', 'valent', 'fabrice', 'fabien', 'nico', 'thomas', 'sylvain', 'tim',
            'karim', 'robin', 'pierre', 'arnaud', 'max', 'luc', 'mike', 'yann', 'oliv', 'yvan', 'jerem', 'michel',
            'mat', 'kev', 'damien', 'vinc', 'eric', 'gilles', 'jona', 'bruno', 'simon', 'adri', 'serge', 'tony',
            'julien', 'quentin', 'leo', 'step', 'gab', 'david', 'paul', 'killian', 'alvaro', 'ronan', 'anto', 'jb',
            'jp', 'jon', 'patrick', 'virgile', 'juju', 'stef', 'franck', 'alan', 'alain', 'albin', 'alban', 'fran',
            'cyril', 'laure', 'phil', 'jacques', 'jack')

    def _common_name(self, name):
        return len(filter(lambda x: x is False,
                map(lambda n: name.lower().find(n)<0, self._common_names))) > 0

    def search_by_region(self, age_min=20, age_max=30, region=1, sex=0):
        return self.search(
            {'age[min]':age_min, 'age[max]':age_max, 'by':'region', 'region':region, "sex":sex})

    def search_by_disance(self, age_min=20, age_max=30, distance=40, sex=0):
        return self.search(
            {'age[min]':age_min, 'age[max]':age_max, 'by':'distance', 'distance[max]':distance, "sex":sex})

    def search(self, criteria=None):
        if criteria is None:
            return []

        # Go to search page
        self._s.get('https://www.adopteunmec.com/mySearch')
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
            self._s.driver.execute_script("return document.body.innerHTML"))
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
                and not self._common_name(l.get_text())]
        return profiles

    def update_db(self, profiles=[], max_p=None, filename='data/justemenemoi.json'):
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
                page = self._s.get(url)
                html = BeautifulSoup(page.content.decode('utf-8', 'xmlcharrefreplace'))

                name= html.find('div', {'class':'username'}).get_text()
                desc = html.find(text='Description').find_parent('div').find('p').get_text()
                shop = html.find(text='Shopping List').find_parent('div').find('p').get_text()
                # Profile Filtering
                if desc.find("non renseign") >= 0 or shop.find("non renseign") >= 0:
                    continue

                img_url = html.find(id='img-current-pic')['src']
                img_name = img_url.split('/')[-1]
                db[uid] = {
                    "profile": url,
                    "name": name,
                    "img": img_name,
                    "age": html.find('span', {'class':'age'}).get_text(),
                    "city": html.find('span', {'class':'city'}).get_text(),
                    "desc": desc,
                    "shop": shop }

                # Download and save profile pic
                pic = self._s.get(img_url, stream=True)
                pic.raw.decode_content=True
                with open("data/pics/" + img_name, 'wb') as f:
                    shutil.copyfileobj(pic.raw, f)

                time.sleep(.5) # Bit of rest...

        # Write back json
        json_s = json.dumps(db) # Dump as a string, to write to file and as JS var
        with open(filename, 'w') as out_f:
            out_f.write(json_s)
        with open(filename + '.js', 'w') as out_f:
            out_f.write("data = ")
            out_f.write(json_s)


import os
def do_crawl():
    os.environ["PYTHONWARNINGS"] = "ignore" # Remove python warnings
    # Read last region from state file
    region = 0
    try:
        with open('aum.cfg', 'r') as cfg:
            region = int(cfg.readline)
    except:
        pass
    region = (region + 1 % 24)

    try:
        web=AuM()
        profiles=web.search_by_region(age_min=25, age_max=50, region=region)
        web.update_db(profiles)
    except:
        pass

    with open('aum.cfg', 'w') as cfg:
        cfg.write(str(region))

if __name__ == '__main__':
    do_crawl()

# Tinder
# x-auth-token	c7ff6484-8fbd-4246-94f0-71b813957c0e
#https://www.facebook.com/fede.rek.7
#https://www.facebook.com/photo.php?fbid=897484456993922&set=a.101328586609517&type=3&source=11&referrer_profile_id=100001971275275
# ID:
#https://www.facebook.com/100001971275275