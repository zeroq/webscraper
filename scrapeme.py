#!/usr/bin/python

import sys
import hashlib
import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import argparse
import re


class ScrapeMe:
    def __init__(self, url, shot=True, source=True, links=True, use_tor=True):
        """initialize scrapeme class
        """
        if not url.startswith('http'):
            self.url = 'http://'+url
        else:
            self.url = url
        self.use_tor = use_tor
        self.shot = shot
        self.source = source
        self.links = links
        self.init_values()

    def set_user_agent(self, ua):
        """set different user-agent
        """
        self.ua = ua
        return True

    def set_storage_base_dir(self, sd):
        """set different storage base dir
        """
        if os.path.exists(sd):
            self.basedir = sd
            self.storage = '%s/%s/%s' % (self.basedir, self.url.replace('http://','').replace('https://','').replace('/', '|'), time.strftime('%Y-%m-%d'))
        else:
            print('base dir does not exist!')
            return False
        return True

    def set_load_timeout(self, lt):
        """set page load timeout
        """
        try:
            self.load_timeout = float(lt)
        except:
            print('timeout needs to be a float value!')
            return False
        return True

    def set_implicit_wait(self, iw):
        """set wait time before screenshot is taken
        """
        try:
            self.imp_wait = float(iw)
        except:
            print('implicit wait needs to be a float vlaue!')
            return False
        return True

    def init_values(self):
        """initialize custom values
        """
        self.ua = 'user-agent=Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
        self.width = 1680
        self.height = 1050
        self.imp_wait = 10
        self.load_timeout= 60.0
        self.basedir = 'web'
        self.storage = '%s/%s/%s' % (self.basedir, self.url.replace('http://','').replace('https://','').replace('/', '|'), time.strftime('%Y-%m-%d'))
        return True

    def init_chrome(self):
        """initialize chrome browser options
        """
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--start-fullscreen')
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument(self.ua)
        if self.use_tor:
            PROXY = "socks5://127.0.0.1:9050"
            chrome_options.add_argument('--proxy-server=%s' % PROXY)
        return chrome_options

    def get_driver(self, chrome_options):
        """create chrome driver
        """
        driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=chrome_options)
        driver.set_window_size(self.width, self.height)
        driver.implicitly_wait(self.imp_wait)
        driver.set_page_load_timeout(self.load_timeout)
        return driver

    def scrape(self):
        """surf to website using selenium and grab html content
        """
        co = self.init_chrome()
        driver = self.get_driver(co)
        try:
            driver.get(self.url)
        except TimeoutException as e:
            print('Page did not load within given timeout.')
            driver.close()
            driver.quit
            return False
        content = driver.page_source
        url_hash = hashlib.md5(self.url.encode('utf8')).hexdigest()
        if self.shot:
            os.makedirs(self.storage, exist_ok=True)
            driver.save_screenshot('%s/screenshot-%s.png' % (self.storage, url_hash))
        if self.source:
            os.makedirs(self.storage, exist_ok=True)
            with open('%s/source-%s.bin' % (self.storage, url_hash), 'w') as fp:
                fp.write(content)
        if self.links:
            re_links = re.compile('href=\"(https{0,1}://(.+?\..+?)/{0,1}.*?)\"')
            ll = re_links.findall(content)
            with open('%s/links-%s.bin' % (self.storage, url_hash), 'w') as fp:
                for entry in ll:
                    scraped_url = entry[0]
                    fp.write(scraped_url+'\r\n')
        driver.close()
        driver.quit()
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='URL to scrape')
    parser.add_argument('--shot', action='store_true', help='take and store screenshot')
    parser.add_argument('--source', action='store_true', help='store source code')
    parser.add_argument('--tor', action='store_true', help='use local tor proxy for connection')
    parser.add_argument('--links', action='store_true', help='extract all links')
    args = parser.parse_args()
    s = ScrapeMe(args.url, shot=args.shot, source=args.source, links=args.links, use_tor=args.tor)
    s.scrape()
    print('URL successfully scraped.')

