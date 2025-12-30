import os
import nbformat
from nbconvert import HTMLExporter
from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    technologies = models.CharField(max_length=200)
    link = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    notebook = models.FileField(upload_to='notebooks/', blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    notebook_html = models.FileField(upload_to='notebooks/html/', blank=True, null=True)

    def get_notebook_html(self):
        if self.notebook:
            notebook_path = self.notebook.path
            try:
                # Charger le fichier notebook
                with open(notebook_path, "r", encoding="utf-8") as f:
                    nb_node = nbformat.read(f, as_version=4)

                # Convertir en HTML
                html_exporter = HTMLExporter()
                html_exporter.exclude_input = False  # Inclure le code des cellules
                notebook_html, _ = html_exporter.from_notebook_node(nb_node)
                return notebook_html
            except Exception as e:
                return f"<p>Erreur lors du chargement du notebook : {str(e)}</p>"
        return "<p>Aucun notebook disponible.</p>"