import json, tqdm, glob

from django.core.management.base import BaseCommand, CommandError
from core.models import Dossier, Etape, Vote, Depute


def find_positions(json_file, position=None):
    if type(json_file) is list:
        for el in json_file:
            yield from find_positions(el, position=position)
    elif type(json_file) is dict:
        if 'parDelegation' in json_file:
            yield {
                'depute': json_file['acteurRef'],
                'position': position,
            }
        else:
            for key in json_file:
                if key == "pours":
                    position = "pour"
                elif key == "contres":
                    position = "contre"
                elif key == "abstentions":
                    position = "abstention"
                yield from find_positions(json_file[key], position=position)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('files', type=str)
        parser.add_argument('tableau_scrutins', type=str)

    def handle(self, *args, **options):
        deputes = {'PA'+dep.identifiant: dep for dep in Depute.objects.all()}
        Vote.objects.all().delete()
        tableau_scrutins = {}
        for line in open(options['tableau_scrutins']):
            scrutin = json.loads(line)
            tableau_scrutins[scrutin["numero"]] = scrutin

        votes = []
        for file in glob.glob(options["files"]):
            json_file = json.load(open(file))['scrutin']
            num = int(json_file["numero"])
            if num in tableau_scrutins:
                infos = tableau_scrutins[num] 
                link_dos = infos["url_dossier"]
                if link_dos:
                    dos_slug = link_dos.split('/')[-1].replace('.asp', '')
                    try:
                        dossier = Dossier.objects.get(slug=dos_slug)
                    except:
                        # print("no match", link_dos)
                        continue
                    titre = json_file['titre']
                    if '(première lecture)' in titre:
                        try:
                            etape = dossier.etape_set.get(titre="AN1-DEBATS-DEC")
                        except:
                            # print("no etape", titre)
                            continue
                        if "l'ensemble du" in titre:
                            for vote in find_positions(json_file):
                                if vote["depute"] in deputes:
                                    votes.append(Vote(
                                        etape=etape,
                                        url_scrutin=infos["url_scrutin"],
                                        depute=deputes[vote["depute"]],
                                        position=vote["position"]
                                    ))
                                else:
                                    # ancien deputé
                                    continue
        print('creating', len(votes), "votes")
        Vote.objects.bulk_create(votes)