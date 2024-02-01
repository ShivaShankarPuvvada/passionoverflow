from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords


# Create your models here.
MALE = 'Male'
FEMALE = 'Female'
OTHER = 'Other'
GENDER_IN_CHOICES = [
    (MALE, 'Male'),
    (FEMALE, 'Female'),
    (OTHER, 'Other'),
]
class User(AbstractUser):

    full_name = models.CharField(max_length=300, blank=True, null=True)
    username = models.CharField(max_length=30, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True, unique=True)
    gender = models.CharField(max_length=6, choices=GENDER_IN_CHOICES, null=True, blank=True)
    country = models.CharField(max_length=120, null=True, blank=True)
    
    USERNAME_FIELD = 'email'  # Use email for authentication
    REQUIRED_FIELDS = ['username']
    def __str__(self):
        return self.username  # You can use username or email as the user's string representation
    

class CustomerCompanyDetails(models.Model):
    company_root_user = models.ForeignKey(User, related_name="company_root_user", on_delete=models.SET_NULL, null=True, blank=True)
    company_user = models.ForeignKey(User, related_name="company_user", on_delete=models.SET_NULL, null=True, blank=True)
    company_name = models.CharField(max_length=300, blank=False, null=False, unique=True)
    company_sub_domain_name = models.CharField(max_length=1000, blank=True, null=True, unique=True)
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    history = HistoricalRecords()
    created_by = models.ForeignKey(User, related_name='company_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='company_updated_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.company_name