from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.db.models import Count
import csv
from .models import Menage, Reponse
from django.core.paginator import Paginator
from .serializers import MenageSerializer
from rest_framework import generics
from .serializers import MenageSerializer
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Liste + Création
class MenageListCreateAPIView(generics.ListCreateAPIView):
    queryset = Menage.objects.all().order_by('-id')
    serializer_class = MenageSerializer


# Détail + Mise à jour + Suppression
class MenageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Menage.objects.all()
    serializer_class = MenageSerializer

@login_required(login_url='/login')
def admin_dashboard(request):
    # filtres simples
    quartier = request.GET.get('quartier') or None
    enqueteur = request.GET.get('enqueteur') or None

    qs = Menage.objects.all().order_by('-date_enquete')

    if quartier:
        qs = qs.filter(village_quartier=quartier)
    if enqueteur:
        qs = qs.filter(nom_enqueteur=enqueteur)

    # stats
    total = qs.count()
    very_vuln = qs.filter(score_total__gte=75).count()
    vuln = qs.filter(score_total__gte=45, score_total__lt=75).count()
    low = qs.filter(score_total__lt=45).count()

    stats = {
        'total': total,
        'total_enquetes': total,
        'very_vuln': very_vuln,
        'vuln': vuln,
        'low': low
    }

    # top priority list
    top_priority = Menage.objects.filter(score_total__gte=75).order_by('-score_total')[:6]

    # dropdowns
    quartiers = Menage.objects.values_list('village_quartier', flat=True).distinct()
    enqueteurs = Menage.objects.values_list('nom_enqueteur', flat=True).distinct()

    # menages list with pagination
    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    menages = page_obj.object_list

    # prepare geo markers for the map
    menages_geo = []
    for m in menages:
        menages_geo.append({
            'lat': m.latitude,
            'lon': m.longitude,
            'popup': f"{m.identite or '-'}<br>{m.village_quartier} • {m.numero_menage}<br>Score: {m.score_total}"
        })

    context = {
        'stats': stats,
        'menages': menages,
        'top_priority': top_priority,
        'quartiers': sorted(list(filter(None, quartiers))),
        'enqueteurs': sorted(list(filter(None, enqueteurs))),
        'menages_geo': menages_geo,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'request': request
    }
    return render(request, 'admin/dashboard.html', context)


def export_menages_csv(request):
    qs = Menage.objects.all().order_by('-date_enquete')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="menages_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['identite','village_quartier','numero_menage','date_enquete','nom_enqueteur','latitude','longitude','score_total','niveau_vulnerabilite'])
    for m in qs:
        writer.writerow([
            m.identite,
            m.village_quartier,
            m.numero_menage,
            m.date_enquete,
            m.nom_enqueteur,
            m.latitude,
            m.longitude,
            m.score_total,
            m.niveau_vulnerabilite
        ])
    return response

# --- Vue : Détail d’un ménage ---
def details_menage(request, menage_id):
    menage = get_object_or_404(Menage, id=menage_id)
    reponses = Reponse.objects.filter(menage=menage).select_related('question')

    return render(request, 'admin/details.html', {
        'menage': menage,
        'reponses': reponses
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("admin_dashboard")  # redirige vers ta page admin
        else:
            return render(request, "login.html", {"error": True})

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")  # redirection vers la page de connexion



