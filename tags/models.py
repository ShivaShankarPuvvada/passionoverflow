from django.db import models
from django.contrib.auth import get_user_model
from accounts import models as account_models
from simple_history.models import HistoricalRecords

User = get_user_model()

# Create your models here.
class Tag(models.Model):
    title = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=2, default="1")  # to active and deactive tags.
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records. this is for developers. When customers delete the record, we don't delete it in our database.
    company = models.ForeignKey(account_models.Company, on_delete=models.PROTECT)
    history = HistoricalRecords()
    created_by = models.ForeignKey(User, related_name='tag_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='tag_updated_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.title