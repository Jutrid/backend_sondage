from django.db import models

# Create your models here.

class Menage(models.Model):
    identite = models.CharField(max_length=255)
    village_quartier = models.CharField(max_length=255)
    numero_menage = models.CharField(max_length=50)
    date_enquete = models.DateField()
    nom_enqueteur = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    score_total = models.IntegerField(default=0)
    niveau_vulnerabilite = models.CharField(max_length=50, choices=[
        ('Très vulnérable', 'Très vulnérable'),
        ('Vulnérable', 'Vulnérable'),
        ('Moins vulnérable', 'Moins vulnérable'),
    ], default='*Moins vulnérable')

    def __str__(self):
        return f"{self.identite} - {self.village_quartier} #{self.numero_menage}"

class Question(models.Model):
    texte = models.CharField(max_length=255)
    poids = models.IntegerField(default=0)

    def __str__(self):
        return self.texte


class Reponse(models.Model):
    menage = models.ForeignKey(Menage, on_delete=models.CASCADE, related_name="reponses")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choix = models.CharField(max_length=255)
    points = models.IntegerField()

    def __str__(self):
        return f"Réponse de {self.menage.identite} à '{self.question.texte}'"
