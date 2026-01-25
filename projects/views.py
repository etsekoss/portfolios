from django.shortcuts import render, get_object_or_404
from django.http import Http404
import os
import chardet
from .models import Project
from django.urls import reverse
import json, hashlib
from urllib.parse import urlparse
from datetime import date
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.utils import timezone
from datetime import date, timedelta
from django.db.models.functions import TruncDate

from .models import PageView


# Vue pour la page d'accueil
def home(request):
    projects = Project.objects.all()

    links = {
        #"github": "https://github.com/etsekoss",
        "linkedin": "https://www.linkedin.com/in/kossivi-etse-98033022a/",
    }

    featured_projects = [
        {
            "title": "Analyse & prédiction du prix du gaz sur Ethereum (TER)",
            "bullets": [
                "Collecte et intégration via APIs REST (Infura, Etherscan) + Google BigQuery.",
                "Orchestration de flux batch avec Azure Data Factory pour fiabiliser les datasets.",
                "Analyse et détection d'anomalies lors des périodes de congestion.",
                "Modèles de ML pour prédire les variations du prix du gaz (quasi temps réel).",
            ],
            "stack": "Python, Pandas, NumPy, scikit-learn, Azure Data Factory, BigQuery, APIs REST",
            "github": None,
            "image": "images/tech/ProjetEther.png",
            "notebook_url": None,
        },
        {
            "title": "Conception d'une base de données — agence de voyage",
            "bullets": [
                "Modélisation conceptuelle & logique (clients, réservations, voyages, prestations).",
                "Implémentation relationnelle et requêtes SQL (insertion, consultation, analyse).",
                "Application des principes d'intégrité et de normalisation.",
            ],
            "stack": "SQL, JMerise",
            "github": None,
            "image": "images/tech/agentVoyage.png",
            "notebook_url": None,
        },
        {
            "title": "Stage Data Scientist - Data Engineer — photovoltaïque & IoT",
            "bullets": [
                "ETL/ELT IoT (PV, batteries, réseau, groupes électrogènes) et structuration des données.",
                "KPIs & dashboards temps réel pour le suivi production/consommation/état équipements.",
                "Automatisation des rapports (-70% temps de reporting) pour la décision opérationnelle.",
                "Intégration de modèles ML dans un LLM interne (Spocky) pour diagnostic & maintenance prédictive.",
            ],
            "stack": "Warp10, WarpScript, Discovery, Python, SQL, Git/GitHub",
            "github": None,
            "image": "images/tech/stageTysilio.png",
            "notebook_url": None,
        },
    ]

    # Associer chaque "featured" à son notebook (si le projet existe en base et a un notebook)
    for fp in featured_projects:
        obj = Project.objects.filter(title=fp["title"]).first()
        if obj and obj.notebook_html:
            fp["notebook_url"] = reverse("notebook_view", args=[obj.id])

    return render(request, "projects/home.html", {
        "projects": projects,
        "featured_projects": featured_projects,
        "links": links,
    })





# Vue pour la page de contact
def contact(request):
    return render(request, 'projects/contact.html')

# Vue pour la page À propos
def about(request):
    return render(request, 'projects/about.html')

# Vue pour la page Blog (MVP)
def blog(request):
    return render(request, 'projects/blog.html')


# Vue pour le tableau de bord
def dashboard(request):
    categories = [
        {'name': 'Machine Learning', 'url': 'machine_learning'},
        {'name': 'Deep Learning', 'url': 'deep_learning'},
        {'name': 'Développement Web', 'url': 'web_development'},
        {'name': 'Data Ingénierie', 'url': 'data_engineering'},
        {'name': 'Développement Mobile', 'url': 'mobile_development'},
        {'name': 'Stages', 'url': 'internships'},
        {'name': 'Autres Projets Professionnels', 'url': 'other_projects'},
    ]
    return render(request, 'projects/dashboard.html', {'categories': categories})

# Vue pour lister les projets
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'projects/project_list.html', {'projects': projects})

# Vue pour une catégorie spécifique
from projects.models import Project

CATEGORY_LABELS = {
    "data-engineering": "Data Ingénierie",
    "machine-learning": "Machine Learning",
    "deep-learning": "Deep Learning",
    "stage": "Stage",
    "web-development": "Développement Web",
    "mobile-development": "Développement Mobile",
    "other-projects": "Autres Projets",
}

# Conversion label -> slug 
CATEGORY_SLUGS = {
    "Data Ingénierie": "data-engineering",
    "Machine Learning": "machine-learning",
    "Deep Learning": "deep-learning",
    "Développement Web": "web-development",
    "Développement Mobile": "mobile-development",
    "Autres Projets": "other-projects",
    "Stage": "stage",
}

def category_view(request, category_name=None, category_slug=None):
    """
    Compatible avec :
    - routes fixes qui passent category_name="Machine Learning"
    - route dynamique /projects/<str:category_name>/ (qui sera en fait un slug)
    """

    # 1. Déterminer le slug réel
    if category_slug:
        slug = category_slug
    elif category_name in CATEGORY_SLUGS:
        slug = CATEGORY_SLUGS[category_name]          
    else:
        slug = category_name                         
    # 2. Filtrer
    projects = Project.objects.filter(category=slug)

    # 3. Libellé affiché
    label = CATEGORY_LABELS.get(slug, category_name or slug)

    # 4. Option 404 si rien et catégorie inconnue
    if not projects.exists() and slug not in CATEGORY_LABELS:
        raise Http404(f"La catégorie '{slug}' n'existe pas.")

    return render(request, "projects/category.html", {
        "projects": projects,
        "category_name": label,
        "category_slug": slug,
    })


# Vue pour afficher un notebook en HTML
def notebook_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    notebook_html_content = "<p>Aucun notebook disponible pour ce projet.</p>"

    if project.notebook_html and os.path.exists(project.notebook_html.path):
        try:
            # Détection de l'encodage du fichier HTML
            with open(project.notebook_html.path, "rb") as f:
                raw_data = f.read()
                detected_encoding = chardet.detect(raw_data)['encoding']

            #  Lecture avec encodage détecté
            with open(project.notebook_html.path, "r", encoding=detected_encoding) as f:
                notebook_html_content = f.read()

            # Ajout du CSS pour harmoniser le style
            css_link = '<link rel="stylesheet" href="/static/css/style.css">'
            notebook_html_content = notebook_html_content.replace("</head>", f"{css_link}</head>", 1)

        except UnicodeDecodeError:
            notebook_html_content = "<p>Erreur lors du décodage du fichier Notebook. Essayez de le réenregistrer en UTF-8.</p>"
        except Exception as e:
            notebook_html_content = f"<p>Erreur : {str(e)}</p>"

    return render(request, 'projects/notebook_view.html', {
        'project': project,
        'notebook_html_content': notebook_html_content,
        'category_name': project.category
    })

# Vue pour afficher les détails d'un projet
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'category_name': project.category,
    })

# Vue pour afficher les technologies
def technologies_view(request):
    technologies = {
        "Langages de Programmation": {
            "slug": "langages-de-programmation",
            "items": ["Java", "Python", "JavaScript", "WarpScript", "SQL", "HTML", "CSS"]
        },
        "Frameworks et Bibliothèques": {
            "slug": "frameworks-et-bibliotheques",
            "items": ["Django", "NumPy", "Pandas", "Scikit-learn", "Matplotlib", "Bootstrap", "Tailwind", "Angular"]
        },
        "Outils et Plateformes": {
            "slug": "outils-et-plateformes",
            "items": ["Azure", "AWS", "Git", "GitHub", "GitLab" "CI/CD" ]
        },
        "Domaines Spécifiques": {
            "slug": "domaines-specifiques",
            "items": ["Machine Learning", "Deep Learning", "REST API"]
        },
    }
    return render(request, 'projects/technologies.html', {'technologies': technologies})

# Vue pour afficher les technologies par catégorie
def technologies_category_view(request, category):
    technologies_by_category = {
        "langages-de-programmation": ["Java", "Python", "JavaScript", "SQL", "HTML / CSS", "WarpScript", "R"],
        "frameworks-et-bibliotheques": ["Django", "NumPy / Pandas / Scipy", "Scikit-learn", "Matplotlib", "Bootstrap", "Tailwind", "PyTorch"],
        "outils-et-plateformes": ["Azure Data Factory", "BigQuery", "APIs(REST)", "Warp10", " Discorvery(SenX)", "AWS", "Git(GitHub/GitLab/Etulab)", "CI/CD (GitLab CI / Etulab)", "Node.js /npm", "Jupiter / Notebooks", "Tableau / Power BI"],
        "domaines-specifiques": ["Data Engineering", "Machine Learning", "Deep Learning", "IoT & Time-Series Analytics", "Data Analytics / KPI / Reporting", "Développement Web Data-driven", "Energy & PV Analytics"]
    }
    technologies = technologies_by_category.get(category)
    if not technologies:
        raise Http404(f"La catégorie '{category}' n'existe pas.")
    return render(request, 'projects/technologies_category.html', {
        'category': category,
        'technologies': technologies
    })

# Vue générale des projets
def projects_hub(request):
    return render(request, "projects/projects_hub.html")


# Affiche contenu de projet si pas de lien Notebook ou GitHub
def web_development(request):
    projects = [
        {
            "title": "Développement d'une application de gestion d'un championnat de football",
            "details": [
                "Développer une application web permettant de gérer et de consulter les données d'un championnat de football (équipes, matchs, résultats, classement).",
                "Mettre en œuvre une architecture web séparant le backend et le frontend avec une API REST Java Spring Boot et une interface Angular.",
                "Structurer le backend selon une architecture en couches (Controllers, Services, Repositories, DTO).",
                "Sécuriser et fiabiliser l'application par des tests automatisés (unitaires et web) et un pipeline CI/CD GitLab déclenchant l'exécution des tests à chaque évolution.",
            ],
            "stack": "Java, Spring Boot, Spring MVC, Spring Data JPA, Spring Security, Angular, TypeScript, HTML/CSS, JUnit, Mockito, Git, GitLab CI/CD, Gradle",
        },

        # Projet Architecture API & 

        {
            "title": "Développement d'une application web de jeu de devinette de mots (Wordle-like)",
            "details": [
                "Conception et développement d'un jeu web interactif où l'utilisateur doit deviner un mot en un nombre limité de tentatives.",
                "Implémentation d'une API REST pour la gestion des niveaux, la validation des mots et le calcul des réponses.",
                "Séparation entre frontend et backend avec échanges JSON et gestion des états applicatifs côté client.",
                "Mise en place de règles de validation, de gestion des erreurs et d'un dictionnaire de mots pour fiabiliser les entrées utilisateur."
            ],
            "stack": "JavaScript (ES6), Node.js, Fastify, API REST, HTML/CSS, Git, Tests automatisés."
        },

    ]

    return render(request, "projects/showcase_static.html", {
        "page_title": "Développement Web",
        "page_subtitle": "Applications, APIs, intégration et outils web orientés usage.",
        "projects": projects,
    })


def mobile_development(request):
    projects = [
        {
            "title": "Application Android — Compression d'image par SVD",
            "details": [
                "Développer une application mobile permettant de compresser des images via la décomposition en valeurs singulières (SVD).",
                "Mettre en place un workflow de sélection d'image, traitement, prévisualisation et export.",
                "Évaluer l'impact de la compression (qualité visuelle / taille fichier).",
            ],
            "stack": "Java, Android Studio, Algèbre linéaire (SVD)",
        },

        # 
        
        {
            "title": "Application mobile — Suivi météo multi-villes (iOS & Android)",
            "details": [
                "Développer une application mobile native permettant de consulter la météo en temps réel pour plusieurs villes.",
                "Intégrer une API REST externe afin de récupérer et mettre à jour les données météorologiques (température, conditions, prévisions).",
                "Concevoir des interfaces réactives avec navigation entre écrans, gestion d'une liste de villes et affichage détaillé des informations.",
                "Mettre en place une persistance locale et une synchronisation contrôlée des données pour limiter les appels réseau."
            ],
            "stack": "SwiftUI, Jetpack Compose (Kotlin), REST API, OpenWeatherMap, JSON, Persistence locale, Git"
        }

    ]

    return render(request, "projects/showcase_static.html", {
        "page_title": "Développement Mobile",
        "page_subtitle": "Android (Kotlin / Java) & iOS (Swift) — apps et intégrations.",
        "projects": projects,
    })

def _get_ref_domain(referrer: str) -> str :
    try:
        if not referrer:
            return ""
        host = urlparse(referrer).netloc.lower()
        return host.replace("www.", "")
    except Exception:
        return ""

def _device_type(user_agent: str) -> str:
    ua = (user_agent or "").lower()
    if "mobile" in ua or "android" in ua or "iphone" in ua:
        return "mobile"
    if ua:
        return "desktop"
    return "other"

def _browser_family(user_agent: str) -> str:
    ua = (user_agent or "").lower()

    if "edg/" in ua or "edga" in ua or "edgios" in ua:
        return "Edge"
    if "firefox/" in ua:
        return "Firefox"
    if "chrome/" in ua and "safari/" in ua and "edg/" not in ua:
        return "Chrome"
    if "safari/" in ua and "chrome/" not in ua:
        return "Safari"
    return "Other"


def _client_ip_truncated(request) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    ip = (xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR", "")) or ""

    # IPv6 : on garde un préfixe grossier (3 hextets)
    if ":" in ip:
        parts = ip.split(":")
        return ":".join(parts[:3]) + "::"

    # IPv4 : on garde /24
    parts = ip.split(".")
    if len(parts) == 4:
        return ".".join(parts[:3]) + ".0"

    return ""


@csrf_exempt
def analytics_collect(request):
    # 1) Opt-out : si refus, on ignore
    if request.COOKIES.get("analytics_optout") == "1":
        return JsonResponse({"ok": True})

    # 2) On accepte seulement POST
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    # 3) Same-origin minimal (si tu veux activer une whitelist)
    referer = request.META.get("HTTP_REFERER", "")
    allowed = getattr(settings, "ANALYTICS_ALLOWED_REFERERS", [])
    if allowed and not any(referer.startswith(a) for a in allowed):
        return JsonResponse({"ok": False}, status=403)

    # 4) Lire JSON
    try:
        payload = json.loads((request.body or b"{}").decode("utf-8"))
    except Exception:
        payload = {}

    path = (payload.get("path") or "")[:255]
    if not path.startswith("/"):
        path = "/" + path

    ref = _get_ref_domain(payload.get("referrer") or "")
    ua = request.META.get("HTTP_USER_AGENT", "")

    device = _device_type(ua)
    browser = _browser_family(ua)

    # 5) Uniques approximatifs (uniquement si SALT défini)
    visitor_day = ""
    salt = getattr(settings, "ANALYTICS_SALT", "")
    if salt:
        ip_trunc = _client_ip_truncated(request)
        day = date.today().isoformat()
        raw = f"{salt}|{day}|{ip_trunc}|{browser}|{device}"
        visitor_day = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    PageView.objects.create(
        path=path,
        ref_domain=ref,
        device_type=device,
        browser=browser,
        visitor_day=visitor_day,
    )

    return JsonResponse({"ok": True})


def analytics_optout(request):
    resp = JsonResponse({"ok": True})
    resp.set_cookie("analytics_optout", "1", max_age=3600*24*400, samesite="Lax")
    return resp

def analytics_optin(request):
    resp = JsonResponse({"ok": True})
    resp.delete_cookie("analytics_optout")
    return resp

def _is_owner(u):
    return u.is_authenticated and u.is_superuser



@login_required
@user_passes_test(_is_owner)
def analytics_dashboard(request):
    # 1) Filtre jours (borné)
    try:
        days = int(request.GET.get("days", "30"))
    except ValueError:
        days = 30
    days = max(1, min(days, 365))

    since = timezone.now() - timedelta(days=days)
    qs = PageView.objects.filter(ts__gte=since)

    # 2) KPIs
    kpi_pageviews = qs.count()
    kpi_uniques = qs.exclude(visitor_day="").values("visitor_day").distinct().count()

    # 3) Tops
    top_pages = qs.values("path").annotate(c=Count("id")).order_by("-c")[:10]
    top_sources = qs.exclude(ref_domain="").values("ref_domain").annotate(c=Count("id")).order_by("-c")[:10]
    devices = qs.exclude(device_type="").values("device_type").annotate(c=Count("id")).order_by("-c")
    browsers = qs.exclude(browser="").values("browser").annotate(c=Count("id")).order_by("-c")

    # 4) Séries pour graphique (pageviews/jour)
    by_day = (
        qs.annotate(day=TruncDate("ts"))
          .values("day")
          .annotate(c=Count("id"))
          .order_by("day")
    )
    by_day_list = list(by_day)
    max_c = max((d["c"] for d in by_day_list), default=1)
    for d in by_day_list:
        d["pct"] = int((d["c"] / max_c) * 100)  # hauteur barre %

    return render(request, "projects/analytics_dashboard.html", {
        "days": days,
        "kpi_pageviews": kpi_pageviews,
        "kpi_uniques": kpi_uniques,
        "top_pages": top_pages,
        "top_sources": top_sources,
        "devices": devices,
        "browsers": browsers,
        "by_day": by_day_list,
    })
