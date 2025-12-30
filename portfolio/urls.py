from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # Import pour les settings
from django.conf.urls.static import static  # Pour les fichiers statiques
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('projects.urls')),  # Inclure les URLs de l'application 'projects'
]

# Ajouter cette ligne pour servir les fichiers médias
if settings.DEBUG:  # Seulement en mode développement
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)