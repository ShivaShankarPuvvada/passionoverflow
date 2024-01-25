from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from accounts import models as account_models
from simple_history.models import HistoricalRecords
from phases import models as phase_models
from tickets import models as ticket_models
from sprints import models as sprint_models
from stages import models as stage_models
from projects import models as project_models
from segments import models as segment_models

User = get_user_model()

# Create your models here.
class Milestone(models.Model):
    title = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=2, default="1")
    company = models.ForeignKey(account_models.CustomerCompanyDetails, on_delete=models.PROTECT)
    history = HistoricalRecords()
    completion_date = models.DateField() # A date milestone is achieved.
    phases = models.ManyToManyField(phase_models.Phase, blank=True)
    tickets = models.ManyToManyField(ticket_models.Ticket, blank=True)
    stages = models.ManyToManyField(stage_models.Stage, blank=True)
    sprints = models.ManyToManyField(sprint_models.Sprint, blank=True)
    project = models.ForeignKey(project_models.Project, on_delete=models.CASCADE, related_name='project_milestones', null=True, blank=True) # project specific milestone
    segment = models.ForeignKey(segment_models.Segment, on_delete=models.CASCADE, related_name='segment_milestones', null=True, blank=True) # segment specific milestone
    created_by = models.ForeignKey(User, related_name='milestone_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='milestone_updated_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.title