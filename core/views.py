from django.http import HttpResponse

from lys import L, raw, render

from core.models import Depute, Dossier, Etape, Vote


HEADER = """
<!DOCTYPE html>
<html lang="fr"><head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Votes des députés</title>
    <link href="https://bootswatch.com/4/lux/bootstrap.min.css" rel="stylesheet">
  </head>

  <body>
    <main role="main" class="container">
      <hr>
      <h1 class="text-center"><a href="/">Votes des députés</a></h1>
      <hr>
"""

FOOTER = """
	<p></p>
    </main>
</body>
</html>
"""

def template(content):
	return render([
		raw(HEADER),
		content,
		raw(FOOTER)
	])

def homepage(request):
	deputes = Depute.objects.all().order_by('nom', 'prenom')
	return HttpResponse(template([
		L.h2 / [
			"Députés ",
			L.small(".text-muted") / " actifs"
		],
		L.div(".list-group") / [
			L.a(".list-group-item.list-group-item-action.flex-column.align-items-start", href=dep.identifiant) / [
				L.div(".d-flex.w-100.justify-content-between") / [
					L.h5(".mb-1") / str(dep)
				]
			]
			for dep in deputes
		]
	]))


def _display_depute_vote(dos, dep):
	votes = Vote.objects.filter(etape__dossier=dos)
	count = votes.count()
	if count > 0:
		try:
			vote = votes.filter(depute=dep).first()
		except:
			vote = None
		if vote:
			if vote.position == 'pour':
				return L.small(".badge.badge-success") / vote.position
			elif vote.position == 'container':
				return L.small(".badge.badge-danger") / vote.position
			elif vote.position == 'abstention':
				return L.small(".badge.badge-warning") / vote.position
		else:
			return L.small(".badge.badge-info") / f"absent(e) sur {count}"


def depute(request, dep_id):
	dep = Depute.objects.get(identifiant=dep_id)
	dossiers = Dossier.objects.filter(date_promulgation__isnull=False).order_by("-date_promulgation", "titre")
	return HttpResponse(template([
		str(dep),
		L.h2 / [
			"Lois",
			L.small(".text-muted") / " promulguées"
		],
		L.div(".list-group") / [
			L.a(".list-group-item.list-group-item-action.flex-column.align-items-start",
				href="/" + dep.identifiant + "/dossier/" + dos.identifiant
			) / [
				L.div(".d-flex.w-100.justify-content-between") / [
					L.h5(".mb-1") / dos.titre,
					_display_depute_vote(dos, dep),
				]
			]
			for dos in dossiers
		]
	]))


def _display_etape_vote(etape, dep):
	count = etape.vote_set.all().count()
	if count > 0:
		try:
			vote = etape.vote_set.get(depute=dep)
		except:
			vote = None
		if vote:
			if vote.position == 'pour':
				return L.small(".badge.badge-success") / vote.position
			elif vote.position == 'container':
				return L.small(".badge.badge-danger") / vote.position
			elif vote.position == 'abstention':
				return L.small(".badge.badge-warning") / vote.position
		else:
			return L.small(".badge.badge-info") / f"absent(e) sur {count}"

def depute_dossier(request, dep_id, dos_id):
	dep = Depute.objects.get(identifiant=dep_id)
	dos = Dossier.objects.get(identifiant=dos_id)
	etapes = Etape.objects.filter(dossier=dos).order_by("-date")
	return HttpResponse(template([
		str(dep),
		" / ",
		str(dos),
		L.h2 / [
			"Étapes",
		],
		L.div(".list-group") / [
			L.a(".list-group-item.list-group-item-action.flex-column.align-items-start",
				href="/" + dep.identifiant + "/etape/" + etape.identifiant
			) / [
				L.div(".d-flex.w-100.justify-content-between") / [
					L.h5(".mb-1") / etape.titre,
					_display_etape_vote(etape, dep),
				]
			]
			for etape in etapes
		]
	]))


def depute_etape(request, dep_id, etape_id):
	dep = Depute.objects.get(identifiant=dep_id)
	etape = Etape.objects.get(identifiant=etape_id)
	dos = etape.dossier
	try:
		vote = etape.vote_set.get(depute=dep)
	except:
		vote = etape.vote_set.first()
	return HttpResponse(template([
		str(dep),
		" / ",
		str(dos),
		" / ",
		str(etape),
		L.p / L.a(href=vote.url_scrutin) / "lien scrutin",
	]))

