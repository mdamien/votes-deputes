import json, tqdm, csv

from django.core.management.base import BaseCommand, CommandError
from core.models import Depute

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
    	Depute.objects.all().delete()
    	deps = []
    	for line in csv.DictReader(open(options['file'])):
    		dep = Depute(
    			identifiant=line['identifiant'],
    			prenom=line['Prénom'],
    			nom=line['Nom'],
    		)
    		deps.append(dep)
    	Depute.objects.bulk_create(deps)