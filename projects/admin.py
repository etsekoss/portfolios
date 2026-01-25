from django.contrib import admin
from .models import Project, PageView

admin.site.register(Project)

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):

    list_display = ("ts", "path", "ref_domain", "device_type", "browser")
    list_filter = ("device_type", "browser", "ref_domain")
    search_fields = ("path", "ref_domain")
    date_hierarchy = "ts"
