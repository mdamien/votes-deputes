from django.db import models


class Depute(models.Model):
	identifiant = models.CharField(max_length=16, primary_key=True)
	prenom = models.CharField(max_length=100)
	nom = models.CharField(max_length=100)

	def __str__(self):
		return f"{self.prenom} {self.nom}"


class Dossier(models.Model):
	identifiant = models.CharField(max_length=16, primary_key=True)
	titre = models.CharField(max_length=200)
	date_promulgation = models.CharField(max_length=40, null=True)

	def __str__(self):
		return self.titre


class Etape(models.Model):
	dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE)
	identifiant = models.CharField(max_length=16, primary_key=True)
	date = models.CharField(max_length=40)
	titre = models.CharField(max_length=200)

	def __str__(self):
		return self.titre
