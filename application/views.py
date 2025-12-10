import json
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.db.models import Count
import csv
from .models import Menage, Reponse, Distribution, Bouquets, Besoin, Articles, ItemDistribution
from django.core.paginator import Paginator
from .serializers import MenageSerializer
from rest_framework import generics
from .serializers import MenageSerializer, DistributionSerializer, BesoinSerializer, BouquetsSerializer, ArticlesSerializer
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
import qrcode
import base64
from io import BytesIO
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Liste + Création
class MenageListCreateAPIView(generics.ListCreateAPIView):
    queryset = Menage.objects.all().order_by('-id')
    serializer_class = MenageSerializer


# Détail + Mise à jour + Suppression
class MenageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Menage.objects.all()
    serializer_class = MenageSerializer

# Liste + Création
class DistributionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Distribution.objects.all().order_by('-id')
    serializer_class = DistributionSerializer

class BesoinListCreateAPIView(generics.ListCreateAPIView):
    queryset = Besoin.objects.all().order_by('-id')
    serializer_class = BesoinSerializer

class BouquetsListCreateAPIView(generics.ListCreateAPIView):
    queryset = Bouquets.objects.all().order_by('-id')
    serializer_class = BouquetsSerializer

class ArticlesListCreateAPIView(generics.ListCreateAPIView):
    queryset = Articles.objects.all().order_by('-id')
    serializer_class = ArticlesSerializer

class DistributionCreateView(APIView):
    def post(self, request):
        serializer = DistributionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Distribution enregistrée"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/login')
def admin_dashboard(request):        
    # Récupération des filtres GET
    air_filter = request.GET.get("air_sante", "")
    enqueteur_filter = request.GET.get("enqueteur", "")
    quartier_filter = request.GET.get("quartier", "")

    # Query de base
    menages = Menage.objects.all()
    for menage in menages:
        if menage.score_total >= 75:
            menage.niveau_vulnerabilite = "Très vulnérable"
            menage.save() 
        elif menage.score_total >= 45:
            menage.niveau_vulnerabilite = "Vulnérable"
            menage.save() 
        else:
            menage.niveau_vulnerabilite = "Moins vulnérable"
            menage.save()

    # Filtre Aire de Santé
    if air_filter:
        menages = menages.filter(air_sante=air_filter)

    # Filtre Enquêteur
    if enqueteur_filter:
        menages = menages.filter(nom_enqueteur=enqueteur_filter)

    # Filtre Quartier
    if quartier_filter:
        menages = menages.filter(village_quartier=quartier_filter)

    # Choix des Aires de Santé
    AIR_SANTE_CHOICES = Menage._meta.get_field("air_sante").choices

    # Liste distincte des quartiers
    quartiers = (
        Menage.objects.values_list("village_quartier", flat=True)
        .distinct()
        .order_by("village_quartier")
    )

    # Liste enquêteurs
    enqueteurs = User.objects.all()

    # Générer données JSON pour Leaflet
    menages_json = json.dumps([
        {
            "id": m.id,
            "identite": m.identite,
            "air_sante": m.air_sante,
            "village_quartier": m.village_quartier,
            "latitude": m.latitude,
            "longitude": m.longitude,
        }
        for m in menages
        if m.latitude and m.longitude
    ])

    # Statistiques pour le graphique (JSON)
    stats_vulnerabilite = {
        "tres_vulnerable": menages.filter(niveau_vulnerabilite="Très vulnérable").count(),
        "vulnerable": menages.filter(niveau_vulnerabilite="Vulnérable").count(),
        "moins_vulnerable": menages.filter(niveau_vulnerabilite="Moins vulnérable").count(),
    }
    stats_vulnerabilite_json = json.dumps(stats_vulnerabilite)

    # Nombre total après application des filtres (pour l'affichage)
    total_menages = menages.count()

    # Pagination: 20 ménages par page
    paginator = Paginator(menages.order_by('-id'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "total_menages": total_menages,
        "menages": page_obj,
        "AIR_SANTE_CHOICES": AIR_SANTE_CHOICES,
        "quartiers": quartiers,
        "enqueteurs": enqueteurs,

        # Filtres actifs
        "air_filter": air_filter,
        "enqueteur_filter": enqueteur_filter,
        "quartier_filter": quartier_filter,

        # Données pour Leaflet
        "menages_json": menages_json,
        # Données pour le graphique (JSON)
        "stats_vulnerabilite_json": stats_vulnerabilite_json,

        "tres_vulnerables": menages.filter(niveau_vulnerabilite="Très vulnérable").count(),
        "vulnerables": menages.filter(niveau_vulnerabilite="Vulnérable").count(),
        "moins_vulnerables": menages.filter(niveau_vulnerabilite="Moins vulnérable").count(),
    }

    return render(request, "admin/dashboard.html", context)

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

def fiche_menage(request, menage_id):
    menage = get_object_or_404(Menage, id=menage_id)

    v = menage.niveau_vulnerabilite
    if v == "Très vulnérable":
        v = 1
    elif v == "Vulnérable":
        v = 2
    else:
        v = 3

    # Texte encodé dans le QR (par exemple l'ID du ménage)
    # Texte encodé dans le QR (uuid et niveau)
    qr_data = {
        "uuid": str(menage.uuid),
        "niveauBesoin": v,
        "identite": menage.identite
    }
    qr_text = json.dumps(qr_data, ensure_ascii=False)

    # Génération du QR Code
    qr = qrcode.make(qr_text)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return render(request, "admin/fiche_menage.html", {
        "menage": menage,
        "qrcode_base64": qr_base64
    })

def gestion_utilisateurs(request):
    groupe_filter = request.GET.get("groupe")

    users = User.objects.all().order_by("id")
    groupes = Group.objects.all()

    if groupe_filter:
        users = users.filter(groups__id=groupe_filter)

    return render(request, "admin/gestion_users.html", {
        "users": users,
        "groupes": groupes,
        "groupe_filter": groupe_filter
    })

def ajouter_utilisateur(request):
    groupes = Group.objects.all()

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        groupe_id = request.POST.get("groupe")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
            return redirect("ajouter_utilisateur")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        if groupe_id:
            groupe = Group.objects.get(id=groupe_id)
            user.groups.add(groupe)

        messages.success(request, "Utilisateur ajouté avec succès.")
        return redirect("gestion_utilisateurs")

    return render(request, "admin/user_form.html", {
        "groupes": groupes,
        "mode": "add"
    })

def modifier_utilisateur(request, user_id):
    user = get_object_or_404(User, id=user_id)
    groupes = Group.objects.all()

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")

        groupe_id = request.POST.get("groupe")
        user.groups.clear()
        if groupe_id:
            groupe = Group.objects.get(id=groupe_id)
            user.groups.add(groupe)

        if request.POST.get("password"):
            user.set_password(request.POST.get("password"))

        user.save()
        messages.success(request, "Modifications enregistrées.")
        return redirect("gestion_utilisateurs")

    return render(request, "admin/user_form.html", {
        "user": user,
        "groupes": groupes,
        "mode": "edit"
    })

def supprimer_utilisateur(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "Utilisateur supprimé.")
    return redirect("gestion_utilisateurs")

def liste_menages(request):
    distribution = Distribution.objects.all().order_by("-id")
    print(distribution)
    return render(request, "admin/liste_menages.html", {"distribution": distribution})

def menage_detail_articles(request, id):
    distribution = get_object_or_404(Distribution, id=id)
    items = ItemDistribution.objects.filter(distribution=distribution)
    print(items)
    return render(request, "admin/detail_articles.html", {
        "distribution": distribution,
        "items": items
    })

