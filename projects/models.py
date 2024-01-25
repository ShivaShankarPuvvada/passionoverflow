from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.auth import get_user_model
from accounts import models as account_models
from phases import models as phase_models

User = get_user_model()

# Create your models here.
class Project(models.Model):
    """
    By default project status is 1. That means project is currently open and running.
    """
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=2, default="1")
    company = models.ForeignKey(account_models.CustomerCompanyDetails, on_delete=models.PROTECT)
    assigned_by = models.ManyToManyField(User, through='ProjectAssignment', related_name='project_assigned_by', through_fields=('project', 'assigned_by'), blank=True)
    assigned_to = models.ManyToManyField(User, through='ProjectAssignment', related_name='project_assigned_to', through_fields=('project', 'assigned_to'), blank=True)
    members = models.ManyToManyField(User, related_name='project_members', blank=True)
    phases = models.ManyToManyField(phase_models.Phase, through='ProjectPhase')
    history = HistoricalRecords()
    created_by = models.ForeignKey(User, related_name='project_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='project_updated_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.title

class ProjectPhase(models.Model):
    """
    This model ProjectPhase will contain all the possible Project-Phase saved relations. 
    Project title is unique.
    There might be mutiple records with the same phase.
    There might be multiple records with same status.
    alpha phase with active status
    alpha phase with deactive status
    beta phase with active status
    beta phase with deactive status
    We will create a new record everytime user make change to the phase for project.
    If user tries to use Same phase with same status, it will not create new record.
    Single project will be associated with only one single phase at a time.
    We need to get the latest record from ProjectPhase table to know which phase is currently assoicated with this project.
    There will always be one active phase associated with the project.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    phase = models.ForeignKey(phase_models.Phase, on_delete=models.CASCADE)
    history = HistoricalRecords()
    status = models.CharField(max_length=2, default="1")
    created_by = models.ForeignKey(User, related_name='projectphase_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='projectphase_updated_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    

class ProjectAssignment(models.Model):
    """
    # Example usage in a view or serializer
    project_instance = Project.objects.get(pk=1)

    # Historical assignments given by project_instance.assigned_by
    assignments_given = project_instance.assigned_by.all()

    # Historical assignments received by project_instance.assigned_to
    assignments_received = project_instance.assigned_to.all()
    
    from .models import Assignment

    # Get the latest assignment for a particular project
    latest_assignment = Assignment.objects.filter(project=project_instance).latest('assigned_at')
    
    from django.core.exceptions import ObjectDoesNotExist

    try:
        latest_assignment = Assignment.objects.filter(project=project_instance).latest('assigned_at')
    except ObjectDoesNotExist:
        # Handle the case where no assignments exist for the project
        latest_assignment = None
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(User, related_name='assignments_given', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(User, related_name='assignments_received', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    created_by = models.ForeignKey(User, related_name='assignment_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='assignment_updated_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)