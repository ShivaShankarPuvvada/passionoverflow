from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.auth import get_user_model
from accounts import models as account_models
from phases import models as phase_models

User = get_user_model()

OPEN = '1'
CLOSED = '0'
STATUS_CHOICES = [
    (OPEN, 'Open'),
    (CLOSED, 'Close'),
]

# Create your models here.
class Project(models.Model):
    """
    Project title is unique.
    """
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=OPEN)
    company = models.ForeignKey(account_models.Company, on_delete=models.PROTECT)
    assigned_by = models.ManyToManyField(User, through='ProjectAssignment', related_name='project_assigned_by', through_fields=('project', 'assigned_by'), blank=True)
    assigned_to = models.ManyToManyField(User, through='ProjectAssignment', related_name='project_assigned_to', through_fields=('project', 'assigned_to'), blank=True)
    members = models.ManyToManyField(User, related_name='project_members', blank=True)
    phases = models.ManyToManyField(phase_models.Phase, through='ProjectPhase', blank=True)
    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='project_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='project_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(Project, self).save(*args, **kwargs)

        if user:
            # self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(Project, self).save()


class ProjectPhase(models.Model):
    """
    This model ProjectPhase will contain all the possible Project-Phase saved relations. 
    There might be multiple records with the same phase.
    There might be multiple records with same status.
    alpha phase with active status
    alpha phase with de-active status
    beta phase with active status
    beta phase with de-active status
    We will create a new record every time user make change to the phase for project.
    If user tries to use Same phase with same status, it will not create new record.
    Single project will be associated with only one single phase at a time.
    We need to get the latest record from ProjectPhase table to know which phase is currently associated with this project.
    There will always be one active phase associated with the project.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    phase = models.ForeignKey(phase_models.Phase, on_delete=models.CASCADE)
    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='projectphase_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='projectphase_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        object_display_message = "Project " + self.project.title + " is in " + self.phase.title + " phase."
        return object_display_message

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(ProjectPhase, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(ProjectPhase, self).save()



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
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='assignment_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='assignment_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        project_assignment = "This project " + str(self.project.title) + " is assigned to " + str(self.assigned_to.get_username) + " by " + str(self.assigned_by.get_username)
        return project_assignment

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(ProjectAssignment, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(ProjectAssignment, self).save()
