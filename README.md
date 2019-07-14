# webscraper
simple python class to instrument python selenium to download html code, take a screenshot and extract hyperlinks 

*  simply run ./scrapeme.py for help:
    * `usage: scrapeme.py [-h] --url URL [--shot] [--source] [--tor] [--links]`
*  when run with any of the additional parameters, it will create a subfolder "web" and store the collected data in another subfolder for the specific url.
*  you can use `--tor` to connect over local tor proxy (default: 127.0.0.1:9050)
