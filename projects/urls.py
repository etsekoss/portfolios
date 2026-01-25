from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Page d'accueil
    path('', views.home, name='home'),

    # Tableau de bord
    path('dashboard/', views.dashboard, name='dashboard'),

    # Technologies
    path('technologies/', views.technologies_view, name='technologies'),
    path('technologies/<str:category>/', views.technologies_category_view, name='technologies_category'),

    # Catégories spécifiques (projets)
    path('projects/machine-learning/', views.category_view, {'category_name': 'Machine Learning'}, name='machine_learning'),
    path('projects/deep-learning/', views.category_view, {'category_name': 'Deep Learning'}, name='deep_learning'),
    #path('projects/web-development/', views.category_view, {'category_name': 'Développement Web'}, name='web_development'),
    path('projects/data-engineering/', views.category_view, {'category_name': 'Data Ingénierie'}, name='data_engineering'),
    #path('projects/mobile-development/', views.category_view, {'category_name': 'Développement Mobile'}, name='mobile_development'),
    path('projects/other-projects/', views.category_view, {'category_name': 'Autres Projets'}, name='other_projects'),
    path("projects/mobile-development/", views.mobile_development, name="mobile_development"),
    path("projects/web-development/", views.web_development, name="web_development"),



    # Liste des projets
    path('projects/', views.project_list, name='project_list'),

    # Pages statiques
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),

    # Page de contact
    path('contact/', views.contact, name='contact'),

    # Détails d'un projet
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),

    # Visualisation du notebook
    path('projects/<int:project_id>/notebook/', views.notebook_view, name='notebook_view'),

    # Vue dynamique pour les catégories (projets généraux)
    path('projects/<str:category_name>/', views.category_view, name='category_view'),

    # 
    path("mes-projets/", views.projects_hub, name="projects_hub"),
    
    # Page analitics
    path("analytics/collect/", views.analytics_collect, name="analytics_collect"),
    path("analytics/optout/", views.analytics_optout, name="analytics_optout"),
    path("analytics/optin/", views.analytics_optin, name="analytics_optin"),
    path("internal/analytics/", views.analytics_dashboard, name="analytics_dashboard"),

]

# Ajoutez les URLs pour les fichiers statiques et médias
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)