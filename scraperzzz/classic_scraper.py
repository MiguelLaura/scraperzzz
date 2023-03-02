# =============================================================================
# Scraper
# =============================================================================
#
# Scraping `https://www.echojs.com`
#

from bs4 import BeautifulSoup
import csv
import os
import re
import requests
from time import sleep
from ural import is_url
from urllib.parse import urljoin


def scraper_echojs(link_scrape, n_pages):
    base_url = 'https://www.echojs.com'
    for i in range(1, n_pages + 1):
        r = requests.get(link_scrape)
        # print('status_code :', r.status_code)
        soup = BeautifulSoup(r.text, 'html.parser')
        for article in soup.select('section article'):
            result = {}
            result['news_id'] = article.get('data-news-id')
            result['text'] = article.select_one('a[rel]').get_text()
            result['link'] = is_url(article.select_one('a[rel]').get('href'))
            if is_url(article.select_one('a[rel]').get('href')):
                result['link'] = article.select_one('a[rel]').get('href')
            result['address'] = article.address.get_text()[3:]
            result['up'] = article.select_one('span:nth-child(1)').get_text()
            result['down'] = article.select_one('span:nth-child(2)').get_text()
            result['user_link'] = urljoin(base_url, article.select_one('username a').get('href'))
            result['user'] = article.select_one('username a').get_text()
            result['time'] = list(article.select_one('p').stripped_strings)[5]
            discuss = article.select_one('p > a').get_text()
            number = re.match('[0-9]+', discuss)
            if number:
                result['number_comments'] = number.group(0)
            result['discuss_link'] = urljoin(base_url, article.select_one('p > a').get('href'))
            if result['link']:
                html = get_html_links_from_scraped(result)
                result['html'] = html[result['news_id']]
            else:
                result['html'] = 'no link'
            yield result
        sleep(0.5)
        link_scrape = link_scrape.rsplit('/', 1)[0] + '/' + str(30 * i)


def get_html_links_from_scraped(result):
    r_link = requests.get(result['link'])
    status = {}
    print('status_code html :', r_link.status_code)
    news_id = result['news_id']
    try:
        r_link.raise_for_status()
        if not os.path.exists("data/echojs"):
            os.makedirs("data/echojs")
        with open('data/echojs/echojs-%s.html' % news_id, 'w') as f_html:
            f_html.write(r_link.text)
            status[news_id] = f'{news_id}.html'
    except requests.exceptions.HTTPError as e:
        print(f'error in {news_id} :', e)
        status[news_id] = e
    return status


if not os.path.exists("data/echojs"):
    os.makedirs("data/echojs")
with open('data/echojs/echojs_latest.csv', 'w') as f:
    fieldnames = ['news_id', 'text', 'link', 'address', 'up', 'down', 'user_link', 'user', 'time', 'number_comments', 'discuss_link', 'html']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    link = 'https://www.echojs.com/latest/0'
    for result in scraper_echojs(link, 3):
        writer.writerow(result)
