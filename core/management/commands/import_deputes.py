import json, tqdm, csv

from django.core.management.base import BaseCommand, CommandError
from core.models import Depute, Etape

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        Depute.objects.all().delete()
        deps = []
        for line in csv.DictReader(open(options['file']), delimiter=';'):
            dep = Depute(
                identifiant=line['id_an'],
                prenom=line['prenom'],
                nom=line['nom_de_famille'],
                actif=line['ancien_depute'] == "0",
                groupe=line['groupe_sigle'],
            )
            deps.append(dep)
        print('creating', len(deps), 'deputes')
        Depute.objects.bulk_create(deps)