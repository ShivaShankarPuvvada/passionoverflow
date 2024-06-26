from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.auth import get_user_model
from projects import models as project_models

User = get_user_model()

OPEN = '1'
CLOSED = '0'
STATUS_CHOICES = [
    (OPEN, 'Open'),
    (CLOSED, 'Close'),
]

# Create your models here.
class Segment(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=OPEN) # this is for customer to make segment deactive
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records. this is for developers. When customers delete the record, we don't delete it in our database.
    project = models.ForeignKey(project_models.Project, related_name='segment_project', on_delete=models.SET_NULL, null=True, blank=True) # one segment belongs to one project only at one time, later we can move it if we want.
    assigned_by = models.ManyToManyField(User, through='SegmentAssignment', related_name='segment_assigned_by', through_fields=('segment', 'assigned_by'), blank=True)
    assigned_to = models.ManyToManyField(User, through='SegmentAssignment', related_name='segment_assigned_to', through_fields=('segment', 'assigned_to'), blank=True)
    members = models.ManyToManyField(User, related_name='segment_members', blank=True)
    history = HistoricalRecords()
    created_by = models.ForeignKey(User, related_name='segment_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='segment_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(Segment, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user


class SegmentAssignment(models.Model):
    """
    # Example usage in a view or serializer
    segment_instance = Project.objects.get(pk=1)

    # Historical assignments given by segment_instance.assigned_by
    assignments_given = segment_instance.assigned_by.all()

    # Historical assignments received by segment_instance.assigned_to
    assignments_received = segment_instance.assigned_to.all()
    
    from .models import Assignment

    # Get the latest assignment for a particular segment
    latest_assignment = Assignment.objects.filter(segment=segment_instance).latest('assigned_at')
    
    from django.core.exceptions import ObjectDoesNotExist

    try:
        latest_assignment = Assignment.objects.filter(segment=segment_instance).latest('assigned_at')
    except ObjectDoesNotExist:
        # Handle the case where no assignments exist for the segment
        latest_assignment = None
    """
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(User, related_name='segment_assignment_given_by', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(User, related_name='segment_assignment_received_to', on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='segment_assignment_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='segment_assignment_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        segment_assignment = "This segment " + str(self.segment.title) + " is assigned to " + str(self.assigned_to.get_username) + " by " + str(self.assigned_by.get_username)
        return segment_assignment

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(SegmentAssignment, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user