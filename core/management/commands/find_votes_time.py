import json, csv

import requests
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from core.models import *


def _find_code_acte(el):
    id = el.get('id', '')
    if id.startswith('acte-'):
        return id.replace(f'acte-{LEGISLATURE}-', '')
    return _find_code_acte(el.parent)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('cache', type=str)

    def handle(self, *args, **options):
        cache_file = options['cache']

        code_lect = 'AN2'
        url = "http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/exploitation_commerciale_image_enfants"

        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')
        for span in list(soup.select('span'))[::-1]:
            doc_id = span.get('data-document-id', '').strip()
            if doc_id.startswith('RUAN'):
                code_acte = _find_code_acte(span)
                if 'DEBATS' in code_acte and code_lect in code_acte:
                    print(span.parent.select_one('a[title="Accéder à la vidéo"]')['href'])
                    print("PARSE VIDEO")
                    return