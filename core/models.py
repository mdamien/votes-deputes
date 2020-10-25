from django.db import models

class Depute(models.Model):
	identifiant = models.CharField(max_length=16, primary_key=True)
	prenom = models.CharField(max_length=100)
	nom = models.CharField(max_length=100)

	def __str__(self):
		return f"{self.prenom} {self.nom}"