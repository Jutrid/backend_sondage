from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.

class Menage(models.Model):
    identite = models.CharField(max_length=255)
    uuid = models.UUIDField(  
        default=uuid.uuid4,      # génère automatiquement un UUID unique
        editable=False            # empêche la modification manuelle
    )
    village_quartier = models.CharField(max_length=255)
    numero_menage = models.CharField(max_length=50, null=True, blank=True)
    date_enquete = models.DateField()
    nom_enqueteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    score_total = models.IntegerField(default=0)
    genre = models.CharField(max_length=10, choices=[
        ('Masculin', 'Masculin'),
        ('Féminin', 'Féminin'),
    ], null=True, blank=True)
    air_sante = models.CharField(max_length=50, choices=[
        ('Yalosase', 'Yalosase'),
        ('Lilanda', 'Lilanda'),
        ('Baonga', 'Baonga'),
        ('Yabasabola', 'Yabasabola'),
        ('Yasanga', 'Yasanga'),
        ('Yakosanga', 'Yakosanga'),
        ('Yafunga', 'Yafunga'),
        ('Lomboto', 'Lomboto'),
        ('Yabongengo', 'Yabongengo'),
        ('Yaelomba', 'Yaelomba'),
    ], null=True, blank=True)
    img = models.ImageField(upload_to='menage_images/', null=True, blank=True)
    adresse = models.CharField(max_length=255, null=True, blank=True)
    niveau_vulnerabilite = models.CharField(max_length=50, null=True, blank=True, choices=[
        ('Très vulnérable', 'Très vulnérable'),
        ('Vulnérable', 'Vulnérable'),
        ('Moins vulnérable', 'Moins vulnérable'),
    ], default='Moins vulnérable')

    def voir_vulnerabilite(self):
        if self.score_total >= 75:
            self.niveau_vulnerabilite = "Très vulnérable"
            self.save()
            return "Très vulnérable"
        elif self.score_total >= 45:
            self.niveau_vulnerabilite = "Vulnérable"
            self.save()
            return "Vulnérable"
        else:
            self.niveau_vulnerabilite = "Moins vulnérable"
            self.save()
            return "Moins vulnérable"

    def __str__(self):
        return f"{self.identite} - {self.village_quartier} #{self.numero_menage}"

    
class Question(models.Model):
    texte = models.CharField(max_length=255)
    poids = models.IntegerField(default=0)

    def __str__(self):
        return self.texte

class Reponse(models.Model):
    menage = models.ForeignKey(Menage, on_delete=models.CASCADE, related_name="reponses")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    choix = models.CharField(max_length=255)
    points = models.IntegerField()

    def __str__(self):
        return f"Réponse de {self.menage.identite} à '{self.question.texte}'"

class Articles(models.Model):
    nom_article = models.CharField(max_length=200)
    quantite = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.nom_article} x{self.quantite}"

class Distribution(models.Model):
    menage_uuid = models.UUIDField(max_length=50, null=True, blank=True)
    date_distribution = models.DateTimeField(auto_now_add=True)
    fournisseurid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="offres_fournies")
    items = models.ManyToManyField(Articles, related_name="offres")
