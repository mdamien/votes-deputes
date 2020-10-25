from django.http import HttpResponse

from lys import L, raw, render

from core.models import Depute, Dossier, Etape


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
				href=dep.identifiant + "/" + dos.identifiant
			) / [
				L.div(".d-flex.w-100.justify-content-between") / [
					L.h5(".mb-1") / dos.titre
				]
			]
			for dos in dossiers
		]
	]))

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
				href=dep.identifiant + "/" + dos.identifiant + "/" + etape.identifiant
			) / [
				L.div(".d-flex.w-100.justify-content-between") / [
					L.h5(".mb-1") / etape.titre
				]
			]
			for etape in etapes
		]
	]))
