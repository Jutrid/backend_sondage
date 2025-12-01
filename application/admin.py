from django.contrib import admin
from .models import Menage, Reponse
# Register your models here.

class MenageAdmin(admin.ModelAdmin):
    list_display = ('identite', 'village_quartier', 'numero_menage', 'date_enquete', 'nom_enqueteur', 'score_total')
    search_fields = ('identite', 'village_quartier', 'numero_menage', 'nom_enqueteur')
    list_filter = ('village_quartier', 'nom_enqueteur', 'date_enquete')

class ReponseAdmin(admin.ModelAdmin):
    list_display = ('menage', 'question', 'choix', 'points')
    search_fields = ('menage__identite', 'question', 'choix')
    list_filter = ('question',)    

admin.site.register(Menage, MenageAdmin)
admin.site.register(Reponse, ReponseAdmin)

