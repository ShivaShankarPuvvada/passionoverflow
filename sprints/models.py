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

"""
Rules for Sprints:
1. If Projects added to sprints, the phase which is associated with projects should be auto filled.
2. If Phase added to sprints, then we should create sprint object with only phase.
3. If Segments added to sprints, the projects and phases should be auto filled.
4. If Tickets added to sprints, the we should auto fill the segment, project and phase.
"""

OPEN = '1'
CLOSED = '0'
STATUS_CHOICES = [
    (OPEN, 'Open'),
    (CLOSED, 'Close'),
]

# Create your models here.
class Sprint(models.Model):
    title = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=OPEN)
    company = models.ForeignKey(account_models.Company, on_delete=models.PROTECT)
    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records. this is for developers. When customers delete the record, we don't delete it in our database.
    start_date = models.DateField() # The date when work on the sprint started.
    end_date = models.DateField() # The date when the sprint was completed or resolved.
    tickets = models.ManyToManyField(ticket_models.Ticket, through='SprintTicket')
    phases = models.ManyToManyField(phase_models.Phase, through='SprintPhase')
    segments = models.ManyToManyField(segment_models.Segment, through='SprintSegment')
    projects = models.ManyToManyField(project_models.Project, through='SprintProject')
    created_by = models.ForeignKey(User, related_name='sprint_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='sprint_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(Sprint, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(Sprint, self).save()


class SprintTicket(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    ticket = models.ForeignKey(ticket_models.Ticket, on_delete=models.CASCADE)

    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='sprintticket_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='sprintticket_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        object_display_message = "Sprint " + self.sprint.title + " is in " + self.ticket.title + " ticket."
        return object_display_message

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(SprintTicket, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(SprintTicket, self).save()


class SprintPhase(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    phase = models.ForeignKey(phase_models.Phase, on_delete=models.CASCADE)

    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='sprintphase_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='sprintphase_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        object_display_message = "Sprint " + self.sprint.title + " is in " + self.phase.title + " ticket."
        return object_display_message

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(SprintPhase, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(SprintPhase, self).save()


class SprintSegment(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    segment = models.ForeignKey(segment_models.Segment, on_delete=models.CASCADE)

    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='sprintsegement_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='sprintsegement_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        object_display_message = "Sprint " + self.sprint.title + " is in " + self.segment.title + " ticket."
        return object_display_message

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(SprintSegment, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(SprintSegment, self).save()


class SprintProject(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    project = models.ForeignKey(project_models.Project, on_delete=models.CASCADE)

    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='sprintproject_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='sprintproject_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        object_display_message = "Sprint " + self.sprint.title + " is in " + self.project.title + " ticket."
        return object_display_message

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(SprintProject, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(SprintProject, self).save()

