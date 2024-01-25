from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.auth import get_user_model
from projects import models as project_models

User = get_user_model()

# Create your models here.
class Segment(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=2, default="1")
    project = models.ForeignKey(project_models.Project, related_name='segment_project', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_by = models.ForeignKey(User, related_name='segment_assigned_by', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ManyToManyField(User, related_name='segment_assigned_to', blank=True)
    members = models.ManyToManyField(User, related_name='segment_members', blank=True)
    history = HistoricalRecords()
    created_by = models.ForeignKey(User, related_name='segment_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='segment_updated_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.title
    
