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
                    titre = infos['objet']
                    codeActe = None
                    if '(première lecture)' in titre:
                        codeActe = "AN1-DEBATS-DEC"
                    if '(deuxième lecture)' in titre:
                        codeActe = "AN2-DEBATS-DEC"
                    if '(texte de la commission mixte paritaire)' in titre:
                        codeActe = "CMP-DEBATS-AN-DEC"
                    if '(nouvelle lecture)' in titre:
                        codeActe = "ANNLEC-DEBATS-DEC"
                    if '(lecture définitive)' in titre:
                        codeActe = "ANLDEF-DEBATS-DEC"
                    if codeActe:
                        try:
                            etape = dossier.etape_set.get(code_acte=codeActe)
                        except:
                            # print("no etape", titre)
                            continue
                        if "l'ensemble d" in titre:
                            for vote in find_positions(json_file):
                                votes.append(Vote(
                                    etape=etape,
                                    url_scrutin=infos["url_scrutin"],
                                    depute=deputes[vote["depute"]],
                                    position=vote["position"]
                                ))
                        elif titre.startswith("l'article"):
                            article = titre.split("l'article")[1].split(' d')[0]
                            for vote in find_positions(json_file):
                                votes.append(Vote(
                                    etape=etape,
                                    article=article,
                                    url_scrutin=infos["url_scrutin"],
                                    depute=deputes[vote["depute"]],
                                    position=vote["position"]
                                ))

        print('creating', len(votes), "votes")
        Vote.objects.bulk_create(votes)