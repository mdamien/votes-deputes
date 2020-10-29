from django.http import HttpResponse
from django.db.models.functions import Lower

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
	deputes = Depute.objects.all().order_by(Lower('nom'), 'prenom')
	return HttpResponse(template([
		raw("""
		<div class="alert alert-dismissible alert-info">
		  <p>Ce site permet de retrouver facilement le votes de vos députés sur les lois et articles des lois</p>
		  <p>Vous pouvez trouver votre député par circonscription sur
		  	 <a href="https://www.nosdeputes.fr/circonscription" class="alert-link">NosDéputés.fr</a></p>
		</div>
		"""),
		L.h2 / [
			"Députés ",
			L.small(".text-muted") / " actifs"
		],
		L.div(".list-group") / [
			L.a(".list-group-item.list-group-item-action.flex-column.align-items-start", href=dep.url()) / [
				L.div(".d-flex.w-100.justify-content-between") / [
					L.h5(".mb-1") / f"{dep.nom}, {dep.prenom}",
				]
			]
			for dep in deputes
		]
	]))


def _display_depute_vote(dos, dep):
	last_vote = Vote.objects.filter(etape__dossier=dos, article__isnull=True).order_by('etape__date').last()
	if last_vote:
		count = last_vote.etape.vote_set.all().count()
	else:
		count = 0
	if count > 0:
		try:
			vote = Vote.objects.filter(etape__dossier=dos, article__isnull=True).order_by('etape__date').filter(depute=dep).last()
		except:
			vote = None
		return _render_vote(vote, count)


def depute(request, dep_id):
	dep = Depute.objects.get(identifiant=dep_id)
	dossiers = Dossier.objects.filter(date_promulgation__isnull=False).order_by("-date_promulgation", "titre")
	return HttpResponse(template([
		_render_breadcrumb([dep]),
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


def _display_etape_vote(etape, dep):
	count = etape.vote_set.filter(article__isnull=True).count()
	if count > 0:
		try:
			vote = etape.vote_set.get(depute=dep)
		except:
			vote = None
		return _render_vote(vote, count)


def depute_dossier(request, dep_id, dos_id):
	dep = Depute.objects.get(identifiant=dep_id)
	dos = Dossier.objects.get(identifiant=dos_id)
	etapes = Etape.objects.filter(dossier=dos).order_by("-date")
	return HttpResponse(template([
		_render_breadcrumb([dep, dos]),
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
	count = etape.vote_set.filter(article=article).count()
	if count > 0:
		try:
			vote = etape.vote_set.filter(article=article, depute=dep).first()
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
		vote = etape.vote_set.filter(article__isnull=True).first()
	except:
		vote = None
	articles = etape.vote_set.values_list('article', flat=True).order_by('article').distinct()
	articles = [a for a in articles if a]
	articles.sort(key=_sort_articles)
	return HttpResponse(template([
		_render_breadcrumb([dep, dos, etape]),
		(
			(
				L.p / L.a(href=vote.url_scrutin) / L.button(".btn.btn-primary") / "lien scrutin"
			) if vote else None
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
	]))


def depute_article(request, dep_id, etape_id, article):
	dep = Depute.objects.get(identifiant=dep_id)
	etape = Etape.objects.get(identifiant=etape_id)
	dos = etape.dossier
	try:
		vote = etape.vote_set.filter(article=article).first()
	except:
		vote = None
	return HttpResponse(template([
		_render_breadcrumb([dep, dos, etape, article]),
		(
			(
				L.p / L.a(href=vote.url_scrutin) / L.button(".btn.btn-primary") / "lien scrutin"
			) if vote else None
		),
	]))

