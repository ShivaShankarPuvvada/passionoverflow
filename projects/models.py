from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.auth import get_user_model
from accounts import models as account_models
from tags import models as tag_models
from phases import models as phase_models
from stages import models as stage_models

User = get_user_model()

# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=2)
    company = models.ForeignKey(account_models.CustomerCompanyDetails, on_delete=models.PROTECT)
    assigned_by = models.ForeignKey(User, related_name='project_assigned_by', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ManyToManyField(User, related_name='project_assigned_to', blank=True)
    members = models.ManyToManyField(User, related_name='project_members', blank=True)
    tags = models.ManyToManyField(tag_models.Tag, related_name='project_tags', blank=True)
    phases = models.ForeignKey(phase_models.Phase, related_name='project_phases', on_delete=models.SET_NULL, null=True, blank=True)
    stages = models.ForeignKey(stage_models.Stage, related_name='project_stages', on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords()
    created_by = models.ForeignKey(User, related_name='project_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='project_updated_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
