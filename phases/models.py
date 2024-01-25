from django.db import models
from django.contrib.auth import get_user_model
from accounts import models as account_models
from simple_history.models import HistoricalRecords

User = get_user_model()

# Create your models here.
class Phase(models.Model):
    """
    Phase can be anything. It may be alpha phase, beta phase, ui/ux phase, developement phase, production phase and etc.
    Phase title is unique.
    For now, for simplicity, we are keeping the phases for project wide. Single project associates with single phase.
    If, in future, requires, we will add the phases to segment level and even ticket level.
    """
    title = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=2, default="1")
    company = models.ForeignKey(account_models.CustomerCompanyDetails, on_delete=models.PROTECT)
    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='phase_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='phase_updated_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.title