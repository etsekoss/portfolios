from django.shortcuts import render, get_object_or_404
from django.http import Http404
import os
import chardet
from .models import Project

# Vue pour la page d'accueil
def home(request):
    # Les projets en base peuvent être utilisés ailleurs (listes/catégories)
    projects = Project.objects.all()

    links = {
        "github": "https://github.com/etsekoss",
        "linkedin": "https://www.linkedin.com/in/kossivi-etse-98033022a/",
    }

    # Projets phares (MVP) — alimentés via des données statiques.
    # Vous pourrez ensuite les stocker en base et les gérer via l'admin.
    featured_projects = [
        {
            "title": "Analyse & prédiction du prix du gaz sur Ethereum (TER)",
            "bullets": [
                "Collecte et intégration via APIs REST (Infura, Etherscan) + Google BigQuery.",
                "Orchestration de flux batch avec Azure Data Factory pour fiabiliser les datasets.",
                "Analyse et détection d’anomalies lors des périodes de congestion.",
                "Modèles de ML pour prédire les variations du prix du gaz (quasi temps réel).",
            ],
            "stack": "Python, Pandas, NumPy, scikit-learn, Azure Data Factory, BigQuery, APIs REST",
            "github": None,
            "category_url": "/projects/data-engineering/",
        },
        {
            "title": "Conception d’une base de données — agence de voyage",
            "bullets": [
                "Modélisation conceptuelle & logique (clients, réservations, voyages, prestations).",
                "Implémentation relationnelle et requêtes SQL (insertion, consultation, analyse).",
                "Application des principes d’intégrité et de normalisation.",
            ],
            "stack": "SQL, JMerise",
            "github": None,
            "category_url": "/projects/data-engineering/",
        },
        {
            "title": "Stage Data Scientist – Data Engineer — photovoltaïque & IoT",
            "bullets": [
                "ETL/ELT IoT (PV, batteries, réseau, groupes électrogènes) et structuration des données.",
                "KPIs & dashboards temps réel pour le suivi production/consommation/état équipements.",
                "Automatisation des rapports (−70% temps de reporting) pour la décision opérationnelle.",
                "Intégration de modèles ML dans un LLM interne (Spocky) pour diagnostic & maintenance prédictive.",
            ],
            "stack": "Warp10, WarpScript, Discovery, Python, SQL, Git/GitHub",
            "github": None,
            "category_url": "/projects/data-engineering/",
        },
    ]

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

    # 1) Déterminer le slug réel
    if category_slug:
        slug = category_slug
    elif category_name in CATEGORY_SLUGS:
        slug = CATEGORY_SLUGS[category_name]          
    else:
        slug = category_name                         
    # 2) Filtrer
    projects = Project.objects.filter(category=slug)

    # 3) Libellé affiché
    label = CATEGORY_LABELS.get(slug, category_name or slug)

    # 4) Option 404 si rien et catégorie inconnue
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
            "items": ["Python", "JavaScript", "SQL", "HTML", "CSS"]
        },
        "Frameworks et Bibliothèques": {
            "slug": "frameworks-et-bibliotheques",
            "items": ["Django", "NumPy", "Pandas", "Scikit-learn", "Matplotlib", "Bootstrap", "Tailwind"]
        },
        "Outils et Plateformes": {
            "slug": "outils-et-plateformes",
            "items": ["Git", "GitHub", "Azure", "AWS"]
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
        "langages-de-programmation": ["Python", "JavaScript", "SQL", "HTML", "CSS"],
        "frameworks-et-bibliotheques": ["Django", "NumPy", "Pandas", "Scikit-learn", "Matplotlib", "Bootstrap", "Tailwind"],
        "outils-et-plateformes": ["Git", "GitHub", "Azure", "AWS"],
        "domaines-specifiques": ["Machine Learning", "Deep Learning", "REST API"]
    }
    technologies = technologies_by_category.get(category)
    if not technologies:
        raise Http404(f"La catégorie '{category}' n'existe pas.")
    return render(request, 'projects/technologies_category.html', {
        'category': category,
        'technologies': technologies
    })