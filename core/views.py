from django.http import HttpResponse
from django.db.models.functions import Lower

from lys import L, raw, render

from core.models import *


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


def _render_breadcrumb(els):

	def _el_url(el):
		nonlocal els
		if hasattr(el, 'url'):
			if el == els[0]:
				return el.url()
			else:
				return el.url(els[0])

	return L.ol(".breadcrumb") / [
		(
			(
				L.li('.breadcrumb-item') / L.a(href=_el_url(el)) / str(el)
			) if el != els[-1] else (
				L.li('.breadcrumb-item.active') / str(el)
			)
		) for el in els
	]


def _render_vote(vote, count):
	if vote:
		if vote.position == 'pour':
			return L.small(".badge.badge-success") / vote.position
		elif vote.position == 'contre':
			return L.small(".badge.badge-danger") / vote.position
		elif vote.position == 'abstention':
			return L.small(".badge.badge-warning") / vote.position
	else:
		return L.small(".badge.badge-info") / f"absent(e) sur {count}"


def homepage(request):
	deputes = Depute.objects.filter(actif=True).order_by(Lower('nom'), 'prenom')
	return HttpResponse(template([
		raw("""
		<div class="alert alert-dismissible alert-info">
		  <p>Ce site permet de retrouver facilement le votes de vos députés sur les lois et articles des lois</p>
		  <p>Vous pouvez trouver votre député par circonscription sur
		  	 <a href="https://www.nosdeputes.fr/circonscription" class="alert-link">NosDéputés.fr</a></p>
		</div>
		"""),
		L.p / L.a(href="/deputes/inactifs") / L.button(".btn.btn-warning") / "voir députés inactifs",
		L.h2 / [
			"Députés ",
			L.small(".text-muted") / " actifs"
		],
		L.div(".list-group") / [
			L.a(".list-group-item.list-group-item-action.flex-column.align-items-start", href=dep.url()) / [
				L.div(".d-flex.w-100.justify-content-between") / [
					L.h5(".mb-1") / f"{dep.nom}, {dep.prenom}",
					L.small / f"{dep.groupe}"
				]
			]
			for dep in deputes
		],
	]))

def deputes_inactifs(request):
	deputes_inactifs = Depute.objects.filter(actif=False).order_by(Lower('nom'), 'prenom')
	return HttpResponse(template([
		L.h2 / [
			"Députés ",
			L.small(".text-muted") / " inactifs"
		],
		L.div(".list-group") / [
			L.a(".list-group-item.list-group-item-action.flex-column.align-items-start", href=dep.url()) / [
				L.div(".d-flex.w-100.justify-content-between") / [
					L.h5(".mb-1") / f"{dep.nom}, {dep.prenom}",
					L.small / f"{dep.groupe}"
				]
			]
			for dep in deputes_inactifs
		]
	]))


def _display_depute_vote(dos, dep):
	last_vote = Vote.objects.filter(scrutin__dossier__isnull=True, scrutin__etape__dossier=dos, scrutin__article__isnull=True).order_by('scrutin__etape__date').last()
	if last_vote:
		count = last_vote.scrutin.vote_set.all().count()
	else:
		count = 0
	if count > 0:
		try:
			vote = Vote.objects.filter(scrutin__dossier__isnull=True, scrutin__etape__dossier=dos, scrutin__article__isnull=True).get(depute=dep)
		except:
			vote = None
		return _render_vote(vote, count)


def depute(request, dep_id):
	dep = Depute.objects.get(identifiant=dep_id)
	dossiers = Dossier.objects.filter(date_promulgation__isnull=False).order_by("-date_promulgation", "titre")
	return HttpResponse(template([
		_render_breadcrumb([dep]),
		L.p / (
			L.a(href=dep.url()+"/lois-en-cours") / L.button(".btn.btn-warning") / "voir lois en cours",
			' ',
			L.a(href=dep.url()+"/autres-votes") / L.button(".btn.btn-warning") / "voir autres votes",
		),
		L.h2 / [
			"Lois",
			L.small(".text-muted") / " promulguées"
		],
		L.div(".list-group") / [
			L.a(".list-group-item.list-group-item-action.flex-column.align-items-start",
				href=dos.url(dep)
			) / [
				L.div(".d-flex.w-100.justify-content-between") / [
					L.h5(".mb-1") / dos.titre,
					_display_depute_vote(dos, dep),
				]
			]
			for dos in dossiers
		]
	]))



def lois_en_cours(request, dep_id):
	dep = Depute.objects.get(identifiant=dep_id)
	dossiers = Dossier.objects.filter(date_promulgation__isnull=True)
	return HttpResponse(template([
		_render_breadcrumb([dep, 'Lois en cours']),
		L.h2 / [
			"Lois",
			L.small(".text-muted") / " en cours d'étude"
		],
		L.div(".list-group") / [
			L.a(".list-group-item.list-group-item-action.flex-column.align-items-start",
				href=dos.url(dep)
			) / [
				L.div(".d-flex.w-100.justify-content-between") / [
					L.h5(".mb-1") / dos.titre,
					_display_depute_vote(dos, dep),
				]
			]
			for dos in dossiers
		]
	]))


def autres_votes(request, dep_id):
	dep = Depute.objects.get(identifiant=dep_id)
	scrutins = Scrutin.objects.filter(dossier__isnull=True, etape__isnull=True)
	return HttpResponse(template([
		_render_breadcrumb([dep, 'Autres votes']),
		L.h2 / [
			"Autres votes",
		],
		L.div(".list-group") / [
			L.a(".list-group-item.list-group-item-action.flex-column.align-items-start",
				href=dep.url()+'/scrutin/'+str(scrutin.id)
			) / [
				L.div(".d-flex.w-100.justify-content-between") / [
					L.h5(".mb-1") / scrutin.objet,
					_display_scrutin_vote(dep, scrutin),
				]
			]
			for scrutin in scrutins
		]
	]))


def _display_etape_vote(etape, dep):
	count = Vote.objects.filter(scrutin__dossier__isnull=True, scrutin__etape=etape, scrutin__article__isnull=True).count()
	if count > 0:
		try:
			vote = Vote.objects.filter(scrutin__dossier__isnull=True, scrutin__etape=etape, scrutin__article__isnull=True).get(depute=dep)
		except:
			vote = None
		return _render_vote(vote, count)


def depute_dossier(request, dep_id, dos_id):
	dep = Depute.objects.get(identifiant=dep_id)
	dos = Dossier.objects.get(identifiant=dos_id)
	etapes = Etape.objects.filter(dossier=dos).order_by("-date")
	return HttpResponse(template([
		_render_breadcrumb([dep, dos]),
		L.p / L.a(href=dos.url_an()) / L.button(".btn.btn-info") / "dossier législatif",
		L.h2 / [
			"Étapes",
		],
		L.div(".list-group") / [
			L.a(".list-group-item.list-group-item-action.flex-column.align-items-start",
				href=etape.url(dep)
			) / [
				L.div(".d-flex.w-100.justify-content-between") / [
					L.h5(".mb-1") / etape.titre,
					_display_etape_vote(etape, dep),
				]
			]
			for etape in etapes
		]
	]))


def _display_article_vote(etape, dep, article):
	count = Vote.objects.filter(scrutin__dossier__isnull=True, scrutin__etape=etape, scrutin__article=article).count()
	if count > 0:
		try:
			vote = Vote.objects.filter(scrutin__dossier__isnull=True, scrutin__etape=etape, scrutin__article=article).get(depute=dep)
		except:
			vote = None
		return _render_vote(vote, count)


def _display_scrutin_vote(dep, scrutin):
	count = scrutin.vote_set.count()
	if count > 0:
		try:
			vote = scrutin.vote_set.get(depute=dep)
		except:
			vote = None
		return _render_vote(vote, count)


def _sort_articles(a):
	try:
		return int(a.split(' ')[0])
	except:
		return 0


def depute_etape(request, dep_id, etape_id):
	dep = Depute.objects.get(identifiant=dep_id)
	etape = Etape.objects.get(identifiant=etape_id)
	dos = etape.dossier
	try:
		scrutin = etape.scrutin_set.filter(dossier__isnull=True, article__isnull=True).first()
	except:
		scrutin = None
	articles = etape.scrutin_set.values_list('article', flat=True).order_by('article').distinct()
	articles = [a for a in articles if a]
	articles.sort(key=_sort_articles)

	scrutins_amendements = etape.scrutin_set.filter(dossier=dos, etape=etape)

	return HttpResponse(template([
		_render_breadcrumb([dep, dos, etape]),
		(
			L.span('.badge.badge-info') / (
				'Le ',
				scrutin.date,
				(
					' ',
					scrutin.heure
				) if scrutin.heure else None,
			),
		) if scrutin else None,
		L.p / (
			(
				' ',
				L.a(href=scrutin.url_an) / L.button(".btn.btn-info") / f'Scrutin',
				(
					' ',
					L.a(href=scrutin.url_video) / L.button(".btn.btn-info") / "video du  vote",
				) if scrutin.url_video else None,
				(
					' ',
					L.a(href=scrutin.url_CR) / L.button(".btn.btn-info") / "compte-rendu",
				) if scrutin.url_CR else None,
			) if scrutin else None
		),
		(
			L.h2 / [
				"Articles",
				L.small(".text-muted") / " votés"
			],
			L.div(".list-group") / [
				L.a(".list-group-item.list-group-item-action.flex-column.align-items-start",
					href="/" + dep.identifiant + "/etape/" + etape.identifiant + "/article/" + article
				) / [
					L.div(".d-flex.w-100.justify-content-between") / [
						L.h5(".mb-1") / f"Article {article}",
						_display_article_vote(etape, dep, article),
					]
				]
				for article in articles
			]
		) if articles else None,
		(
			L.br,
			L.br,
			L.h2 / [
				"Amendements et motions",
				L.small(".text-muted") / " votés"
			],
			L.div(".list-group") / [
				L.a(".list-group-item.list-group-item-action.flex-column.align-items-start",
					href="/" + dep.identifiant + "/scrutin/" + str(amdt_scrutin.id)
				) / [
					L.div(".d-flex.w-100.justify-content-between") / [
						L.h5(".mb-1") / f"{amdt_scrutin.objet}",
						_display_scrutin_vote(dep, amdt_scrutin),
					]
				]
				for amdt_scrutin in scrutins_amendements
			]
		) if scrutins_amendements.count() else None,
	]))


def depute_article(request, dep_id, etape_id, article):
	dep = Depute.objects.get(identifiant=dep_id)
	etape = Etape.objects.get(identifiant=etape_id)
	dos = etape.dossier
	try:
		scrutin = etape.scrutin_set.filter(article=article).first()
	except:
		scrutin = None
	return HttpResponse(template([
		_render_breadcrumb([dep, dos, etape, article]),
		(
			L.span('.badge.badge-info') / (
				'Le ',
				scrutin.date,
				(
					' ',
					scrutin.heure
				) if scrutin.heure else None,
			),
		) if scrutin else None,
		(
			(
				L.p / L.a(href=scrutin.url_an) / L.button(".btn.btn-info") / "scrutin"
			) if scrutin else None
		),
	]))



def depute_scrutin(request, dep_id, scrutin_id):
	dep = Depute.objects.get(identifiant=dep_id)
	scrutin = Scrutin.objects.get(id=scrutin_id)
	return HttpResponse(template([
		_render_breadcrumb([dep, scrutin.dossier, scrutin.etape, scrutin.objet]),
		L.span('.badge.badge-info') / (
			'Le ',
			scrutin.date,
			(
				' ',
				scrutin.heure
			) if scrutin.heure else None,
		),
		(
			(
				L.p / L.a(href=scrutin.url_an) / L.button(".btn.btn-info") / "scrutin"
			) if scrutin else None
		),
	]))



def top_pour(request):
	results = []
	for dep in Depute.objects.all():
		c = Vote.objects.filter(scrutin_dossier=None, scrutin__article__isnull=True, depute=dep, position='pour').count()
		results.append([dep, c])

	results.sort(key=lambda r:-r[1])
	lines = []
	for i, r in enumerate(results):
		dep, c = r
		lines.append(
			L.span(".list-group-item.list-group-item-action.flex-column.align-items-start") / 
				f"{i+1}: {dep} ({dep.groupe}) avec {c} votes pour")
	return HttpResponse(template([
		L.h2 / "Top des députés qui ont votés pour les lois promulguées",
		L.div(".list-group") / lines,
	]))


def top_pour_pourcentage(request):
	results = []
	for dep in Depute.objects.all():
		c = Vote.objects.filter(scrutin_dossier=None, scrutin__article__isnull=True, depute=dep, position='pour').count()
		c2 = Vote.objects.filter(scrutin_dossier=None, scrutin__article__isnull=True, depute=dep).count()
		if c2:
			results.append([dep, c/c2, c])
		else:
			results.append([dep, 0, 0])

	results.sort(key=lambda r: (-r[1], -r[2]))
	lines = []
	for i, r in enumerate(results):
		dep, c, c2 = r
		lines.append(
			L.span(".list-group-item.list-group-item-action.flex-column.align-items-start") / 
				f"{i+1}: {dep} ({dep.groupe}) avec {round(c*100, 2)}% de votes pour ({c2} votes)")
	return HttpResponse(template([
		L.h2 / "Top des députés qui ont votés pour les lois promulguées",
		L.div(".list-group") / lines,
	]))


def top_contre_pourcentage(request):
	results = []
	for dep in Depute.objects.all():
		c = Vote.objects.filter(scrutin_dossier=None, scrutin__article__isnull=True, depute=dep, position='contre').count()
		c2 = Vote.objects.filter(scrutin_dossier=None, scrutin__article__isnull=True, depute=dep).count()
		if c2:
			results.append([dep, c/c2, c])
		else:
			results.append([dep, 0, 0])

	results.sort(key=lambda r: (-r[1], -r[2]))
	lines = []
	for i, r in enumerate(results):
		dep, c, c2 = r
		lines.append(
			L.span(".list-group-item.list-group-item-action.flex-column.align-items-start") / 
				f"{i+1}: {dep} ({dep.groupe}) avec {round(c*100, 2)}% de votes contre ({c2} votes)")
	return HttpResponse(template([
		L.h2 / "Top des députés qui ont votés contre les lois promulguées",
		L.div(".list-group") / lines,
	]))



def top_contre(request):
	results = []
	for dep in Depute.objects.all():
		c = Vote.objects.filter(scrutin_dossier=None, scrutin__article__isnull=True, depute=dep, position='contre').count()
		results.append([dep, c])

	results.sort(key=lambda r:-r[1])
	lines = []
	for i, r in enumerate(results):
		dep, c = r
		lines.append(
			L.span(".list-group-item.list-group-item-action.flex-column.align-items-start") / 
				f"{i+1}: {dep} ({dep.groupe}) avec {c} votes contre")
	return HttpResponse(template([
		L.h2 / "Top des députés qui ont votés contre les lois promulguées",
		L.div(".list-group") / lines,
	]))




def top_pour_lois(request):
	results = []
	for dossier in Dossier.objects.filter(date_promulgation__isnull=False):
		c = 0
		c = Vote.objects.filter(scrutin_dossier=None, scrutin__etape__dossier=dossier, position='pour').count()
		c2 = Vote.objects.filter(scrutin_dossier=None, scrutin__etape__dossier=dossier).count()
		if c2:
			results.append([dossier, c/c2, c])
		else:
			results.append([dossier, 0, 0])

	results.sort(key=lambda r: (-r[1], -r[2]))
	lines = []
	for i, r in enumerate(results):
		dossier, c, c2 = r
		lines.append(
			L.span(".list-group-item.list-group-item-action.flex-column.align-items-start") / 
				f"{i+1}: {dossier} avec {round(c*100, 2)}% de votes pour ({c2} votes)")
	return HttpResponse(template([
		L.h2 / "Top des lois promulguées par le pourcentage de votes pour",
		L.div(".list-group") / lines,
	]))

