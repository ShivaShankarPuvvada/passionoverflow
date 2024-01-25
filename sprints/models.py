from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from accounts import models as account_models
from simple_history.models import HistoricalRecords
from phases import models as phase_models
from tickets import models as ticket_models
from projects import models as project_models
from segments import models as segment_models

User = get_user_model()

# Create your models here.
class Sprint(models.Model):
    title = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=2, default="1")
    company = models.ForeignKey(account_models.CustomerCompanyDetails, on_delete=models.PROTECT)
    history = HistoricalRecords()
    start_date = models.DateField() # The date when work on the sprint started.
    end_date = models.DateField() # The date when the sprint was completed or resolved.
    tickets = models.ManyToManyField(ticket_models.Ticket, through='SprintTicket')
    phases = models.ManyToManyField(phase_models.Phase, through='SprintPhase')
    segments = models.ManyToManyField(segment_models.Segment, through='SprintSegment')
    projects = models.ManyToManyField(project_models.Project, through='SprintProject')
    created_by = models.ForeignKey(User, related_name='sprint_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='sprint_updated_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.title
    

class SprintTicket(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    ticket = models.ForeignKey(ticket_models.Ticket, on_delete=models.CASCADE)

class SprintPhase(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    phase = models.ForeignKey(phase_models.Phase, on_delete=models.CASCADE)

class SprintSegment(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    segment = models.ForeignKey(segment_models.Segment, on_delete=models.CASCADE)
    
class SprintProject(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    project = models.ForeignKey(project_models.Project, on_delete=models.CASCADE)