import json, tqdm, glob

from django.core.management.base import BaseCommand, CommandError
from core.models import Dossier, Etape


def find_date_promulgation(json_dos):
    if type(json_dos) is dict:
        if "infoJO" in json_dos:
            return json_dos["infoJO"]["dateJO"]
        if "acteLegislatif" in json_dos:
            return find_date_promulgation(json_dos["acteLegislatif"])
        if "actesLegislatifs" in json_dos:
            return find_date_promulgation(json_dos["actesLegislatifs"])
    elif type(json_dos) is list:
        for el in json_dos:
            date = find_date_promulgation(el)
            if date:
                return date


def find_etapes(json_dos):
    if type(json_dos) is dict:
        if "textesAssocies" in json_dos or "texteAssocie" in json_dos:
            yield {
                "identifiant": json_dos["uid"],
                "titre": json_dos["codeActe"],
                "date": json_dos["dateActe"],
            }
        if "acteLegislatif" in json_dos:
            yield from find_etapes(json_dos["acteLegislatif"])
        if "actesLegislatifs" in json_dos:
            yield from find_etapes(json_dos["actesLegislatifs"])
    elif type(json_dos) is list:
        for el in json_dos:
            yield from find_etapes(el)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('files', type=str)

    def handle(self, *args, **options):
        Dossier.objects.all().delete()
        Etape.objects.all().delete()
        doslegs = []
        etapes = []
        for file in glob.glob(options["files"]):
            json_dos = json.load(open(file))['dossierParlementaire']
            dos = Dossier(
                identifiant=json_dos['uid'],
                titre=json_dos['titreDossier']['titre'],
                date_promulgation=find_date_promulgation(json_dos),
            )
            for etape in find_etapes(json_dos):
                etape["identifiant"] = dos.identifiant + "-" + etape["identifiant"]
                etapes.append(Etape(
                    dossier=dos,
                    **etape,
                ))
            doslegs.append(dos)
        Dossier.objects.bulk_create(doslegs)
        Etape.objects.bulk_create(etapes)
