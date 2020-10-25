import json, tqdm, glob

from django.core.management.base import BaseCommand, CommandError
from core.models import Dossier

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('files', type=str)

    def handle(self, *args, **options):
        Dossier.objects.all().delete()
        doslegs = []
        for file in glob.glob(options["files"]):
            json_dos = json.load(open(file))['dossierParlementaire']
            dos = Dossier(
                identifiant=json_dos['uid'],
                titre=json_dos['titreDossier']['titre'],
            )
            doslegs.append(dos)
        Dossier.objects.bulk_create(doslegs)
