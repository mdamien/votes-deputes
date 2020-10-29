from django.db import models


class Depute(models.Model):
	identifiant = models.CharField(max_length=16, primary_key=True)
	prenom = models.CharField(max_length=100)
	nom = models.CharField(max_length=100)
	actif = models.BooleanField()

	def url(self):
		return '/' + self.identifiant

	def __str__(self):
		return f"{self.prenom} {self.nom}"


class Dossier(models.Model):
	identifiant = models.CharField(max_length=16, primary_key=True)
	titre = models.CharField(max_length=200)
	slug = models.CharField(max_length=200, null=True)
	date_promulgation = models.CharField(max_length=40, null=True)

	def url(self, dep):
		return dep.url() + "/dossier/" + self.identifiant

	def __str__(self):
		return self.titre


class Etape(models.Model):
	identifiant = models.CharField(max_length=16, primary_key=True) # could be codeActe
	dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE)
	date = models.CharField(max_length=40)
	code_acte = models.CharField(max_length=40)
	titre = models.CharField(max_length=200)

	def url(self, dep):
		return dep.url() + '/etape/' + self.identifiant

	def __str__(self):
		return self.titre

class Vote(models.Model):
	etape = models.ForeignKey(Etape, on_delete=models.CASCADE)
	article = models.CharField(max_length=16, null=True)
	depute = models.ForeignKey(Depute, on_delete=models.CASCADE)
	position = models.CharField(max_length=16)
	url_scrutin = models.CharField(max_length=200)
