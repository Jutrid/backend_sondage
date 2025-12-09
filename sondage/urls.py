"""
URL configuration for sondage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from sondage import settings
from application.views import admin_dashboard
from application import views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API endpoints
    path('api/menages/', views.MenageListCreateAPIView.as_view(), name='menage-list-create'),
    path('api/menages/<int:pk>/', views.MenageDetailAPIView.as_view(), name='menage-detail'),
    path('api/distributions/', views.DistributionListCreateAPIView.as_view(), name='distribution-list-create'),
    path('api/besoins/', views.BesoinListCreateAPIView.as_view(), name='articles-list-create'),
    path('api/bouquets/', views.BouquetsListCreateAPIView.as_view(), name='bouquets-list-create'),

    # Admin and user views
    path('', admin_dashboard, name='admin_dashboard'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('login/', views.login_view, name='login'),
    path("menage/<int:menage_id>/fiche/", views.fiche_menage, name="fiche_menage"),
    path("logout/", views.logout_view, name="logout"),
    path('export-menages-csv/', views.export_menages_csv, name='export_menages_csv'),
    path('menage/<int:menage_id>/details/', views.details_menage, name='details_menage'),
    path("menages/", views.liste_menages, name="liste_menages"),
    path("menages/<int:id>/articles/", views.menage_detail_articles),

    # Utilisateurs
    path('users/', views.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('users/add/', views.ajouter_utilisateur, name='ajouter_utilisateur'),
    path('users/edit/<int:user_id>/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('users/delete/<int:user_id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),

    # --- Schéma OpenAPI ---
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # --- Documentation Swagger ---
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # --- Documentation Redoc ---
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

