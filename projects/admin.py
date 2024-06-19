from django.contrib import admin

from .models import Project, ProjectPhase, ProjectAssignment

# Register your models here.
admin.site.register(Project)
admin.site.register(ProjectPhase)
admin.site.register(ProjectAssignment)