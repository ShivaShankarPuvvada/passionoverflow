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
class Stage(models.Model):
    title = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=OPEN) # to active and deactive stages.
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records. this is for developers. When customers delete the record, we don't delete it in our database.
    company = models.ForeignKey(account_models.Company, on_delete=models.PROTECT)
    history = HistoricalRecords()
    created_by = models.ForeignKey(User, related_name='stage_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='stage_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(Stage, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(Stage, self).save()
