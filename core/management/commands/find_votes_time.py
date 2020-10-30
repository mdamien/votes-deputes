import json, csv, time
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import requests
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from core.models import *

PARSE_JS = """
var links = document.querySelectorAll('.mediaIndex a')
var player = document.querySelector('#html5_player')

var results = []

var i = 0;
function next() {
    if (links[i]) {
        links[i].click()
        setTimeout(() => {
            var result = [player.currentTime, links[i].innerText, links[i].className];
            results.push(result)
            console.log(i, result)
            i += 1
            next()
        }, 2000)
    } else {
        document.body.innerText = JSON.stringify(results)
    }
}
next()
"""


def _find_code_acte(el):
    id = el.get('id', '')
    if id.startswith('acte-'):
        return id.replace(f'acte-{LEGISLATURE}-', '')
    return _find_code_acte(el.parent)


def _parse_video(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(20)
    driver.execute_script(PARSE_JS)
    while True:
        content = driver.find_element_by_tag_name('body').get_attribute('innerText')
        try:
            content = json.loads(content)
            break
        except:
            time.sleep(2)
    driver.quit()

    transformed = []

    prev_time = None
    for el in content:
        new_el = {}
        new_el['time'] = str(datetime.timedelta(seconds=el[0])).split('.')[0]
        if new_el['time'] == prev_time:
            continue
        prev_time = new_el['time']
        new_el['titre'] = el[1]
        new_el['level'] = int(el[2].split('level')[1])
        transformed.append(new_el)

    return transformed


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('cache', type=str)

    def handle(self, *args, **options):
        cache_file = options['cache']


        url = "http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/exploitation_commerciale_image_enfants"
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')


        code_lect = 'AN2'
        for span in list(soup.select('span'))[::-1]:
            doc_id = span.get('data-document-id', '').strip()
            if doc_id.startswith('RUAN'):
                code_acte = _find_code_acte(span)
                if 'DEBATS' in code_acte and code_lect in code_acte:
                    url_video = span.parent.select_one('a[title="Accéder à la vidéo"]')['href']
                    print(url_video)
                    print(json.dumps(_parse_video(url_video), indent=2, ensure_ascii=False))
                    return