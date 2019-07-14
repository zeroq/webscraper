#!/usr/bin/python

import sys
import hashlib
import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FOptions
from selenium.common.exceptions import TimeoutException
import argparse
import re


class ScrapeMe:
    def __init__(self, shot=True, source=True, links=True, use_tor=True, use_chrome=False):
        """initialize scrapeme class
        """
        self.use_tor = use_tor
        self.shot = shot
        self.source = source
        self.links = links
        self.scraped_links = []
        self.init_values()
        self.use_chrome = use_chrome

    def set_user_agent(self, ua):
        """set different user-agent
        """
        self.ua = ua
        return True

    def set_storage_base_dir(self, sd, create=False):
        """set different storage base dir
        """
        if os.path.exists(sd):
            self.basedir = sd
        else:
            if create:
                os.makedirs(sd, exist_ok=True)
                self.basedir = sd
                return True
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
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.javascript': 2})
        chrome_options.add_experimental_option("prefs",{"profile.default_content_setting_values.notifications" : 2})
        chrome_options.add_argument(self.ua)
        if self.use_tor:
            PROXY = "socks5://127.0.0.1:9050"
            chrome_options.add_argument('--proxy-server=%s' % PROXY)
        return chrome_options

    def get_driver_chrome(self, chrome_options):
        """create chrome driver
        """
        driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=chrome_options)
        driver.set_window_size(self.width, self.height)
        driver.implicitly_wait(self.imp_wait)
        driver.set_page_load_timeout(self.load_timeout)
        return driver

    def init_firefox(self):
        """initialize firefox browser options
        """
        ff_profile = webdriver.FirefoxProfile()
        if self.use_tor:
            ff_profile.set_preference("network.proxy.type", 1)
            ff_profile.set_preference("network.proxy.socks", "127.0.0.1")
            ff_profile.set_preference("network.proxy.socks_port", 9050)
            ff_profile.set_preference("network.proxy.socks_remote_dns", True)

        ff_profile.set_preference("media.volume_scale", "0.0");
        ff_profile.accept_untrusted_certs = True
        ff_profile.set_preference("javascript.enabled", False)

        firefox_options = FOptions()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument('--start-maximized')
        firefox_options.add_argument('--start-fullscreen')
        firefox_options.add_argument('--mute-audio')
        firefox_options.add_argument('--ignore-certificate-errors')
        firefox_options.preferences.update({"javascript.enabled": False,})
        firefox_options.set_preference("general.useragent.override", self.ua)

        return firefox_options, ff_profile

    def get_driver_firefox(self, firefox_options, ff_profile):
        """create firefox driver
        """
        driver = webdriver.Firefox(executable_path='./geckodriver', firefox_options=firefox_options, firefox_profile=ff_profile)
        driver.set_window_size(self.width, self.height)
        driver.implicitly_wait(self.imp_wait)
        driver.set_page_load_timeout(self.load_timeout)
        return driver

    def get_links(self):
        """return scraped links
        """
        return self.scraped_links

    def get_storage(self):
        """get storage directory of last url
        """
        return self.storage

    def get_url_hash(self):
        """get hash of last url
        """
        return self.url_hash

    def scrape(self, url):
        """surf to website using selenium and grab html content
        """
        self.scraped_links = []
        if not url.startswith('http'):
            self.url = 'http://'+url
        else:
            self.url = url
        self.storage = '%s/%s/%s' % (self.basedir, self.url.replace('http://','').replace('https://','').replace('/', '|'), time.strftime('%Y-%m-%d'))
        if self.use_chrome:
            co = self.init_chrome()
            driver = self.get_driver_chrome(co)
        else:
            fo, fp = self.init_firefox()
            driver = self.get_driver_firefox(fo, fp)
        try:
            driver.get(self.url)
        except TimeoutException as e:
            print('Page did not load within given timeout.')
            driver.close()
            driver.quit
            return False
        content = driver.page_source
        self.url_hash = hashlib.md5(self.url.encode('utf8')).hexdigest()
        if self.shot:
            os.makedirs(self.storage, exist_ok=True)
            driver.save_screenshot('%s/screenshot-%s.png' % (self.storage, self.url_hash))
        if self.source:
            os.makedirs(self.storage, exist_ok=True)
            with open('%s/source-%s.bin' % (self.storage, self.url_hash), 'w') as fp:
                fp.write(content)
        if self.links:
            re_links = re.compile('href=\"(https{0,1}://(.+?\..+?)/{0,1}.*?)\"')
            ll = re_links.findall(content)
            with open('%s/links-%s.bin' % (self.storage, self.url_hash), 'w') as fp:
                for entry in ll:
                    scraped_url = entry[0]
                    fp.write(scraped_url+'\r\n')
                    self.scraped_links.append(scraped_url)
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
    s = ScrapeMe(shot=args.shot, source=args.source, links=args.links, use_tor=args.tor)
    s.scrape(args.url)
    print('URL successfully scraped.')

