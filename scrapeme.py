#!/usr/bin/python

import sys
import hashlib
import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

if __name__ == '__main__':
    url = sys.argv[1]
    if not url.startswith('http'):
        url = 'http://'+url
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--start-fullscreen")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36")

    storage = 'web/%s/%s' % (url.replace('http://','').replace('https://','').replace('/', '|'), time.strftime('%Y-%m-%d'))
    os.makedirs(storage, exist_ok=True)
    width = 1680
    height = 1050
    driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=chrome_options)
    driver.set_window_size(width, height)
    driver.implicitly_wait(10)
    driver.get(url)
    url_hash = hashlib.md5(url.encode('utf8')).hexdigest()
    content = driver.page_source
    driver.save_screenshot('%s/screenshot-%s.png' % (storage, url_hash))
    with open('%s/source-%s.bin' % (storage, url_hash), 'w') as fp:
        fp.write(content)

    driver.close()
    driver.quit()

