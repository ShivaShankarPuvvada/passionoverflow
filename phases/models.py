from django.db import models
from django.contrib.auth import get_user_model
from accounts import models as account_models
from simple_history.models import HistoricalRecords

User = get_user_model()

OPEN = '1'
CLOSED = '0'
STATUS_CHOICES = [
    (OPEN, 'Open'),
    (CLOSED, 'Close'),
]


# Create your models here.
class Phase(models.Model):
    """
    Phase can be anything. It may be alpha phase, beta phase, ui/ux phase, developement phase, production phase and etc.
    Phase title is unique.
    For now, for simplicity, we are keeping the phases for project wide. Single project associates with single phase.
    If, in future, requires, we will add the phases to segment level and even ticket level.
    """
    title = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=OPEN)
    company = models.ForeignKey(account_models.Company, on_delete=models.PROTECT)
    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='phase_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='phase_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(Phase, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user

