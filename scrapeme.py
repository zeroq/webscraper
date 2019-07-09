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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='URL to scrape')
    parser.add_argument('--shot', action='store_true', help='take and store screenshot')
    parser.add_argument('--source', action='store_true', help='store source code')
    parser.add_argument('--tor', action='store_true', help='use local tor proxy for connection')
    args = parser.parse_args()
    url = args.url
    if not url.startswith('http'):
        url = 'http://'+url
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--start-fullscreen")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36")
    if args.tor:
        PROXY = "socks5://127.0.0.1:9050"
        chrome_options.add_argument('--proxy-server=%s' % PROXY)

    storage = 'web/%s/%s' % (url.replace('http://','').replace('https://','').replace('/', '|'), time.strftime('%Y-%m-%d'))
    os.makedirs(storage, exist_ok=True)
    width = 1680
    height = 1050
    driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=chrome_options)
    driver.set_window_size(width, height)
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(15.0)
    try:
        driver.get(url)
    except TimeoutException as e:
        print('Page did not load within given timeout.')
        driver.close()
        driver.quit
        sys.exit(255)
    url_hash = hashlib.md5(url.encode('utf8')).hexdigest()
    content = driver.page_source
    if args.shot:
        driver.save_screenshot('%s/screenshot-%s.png' % (storage, url_hash))
    if args.source:
        with open('%s/source-%s.bin' % (storage, url_hash), 'w') as fp:
            fp.write(content)
    print('URL successfully scraped.')
    driver.close()
    driver.quit()

