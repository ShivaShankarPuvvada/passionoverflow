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
    """
    Gender and Country will be saved. This is optional for now.
    """

    full_name = models.CharField(max_length=300, blank=True, null=True)
    password = models.CharField(max_length=300, blank=True, null=True)
    username = models.CharField(max_length=30, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True, unique=True)
    gender = models.CharField(max_length=6, choices=GENDER_IN_CHOICES, null=True, blank=True)
    country = models.CharField(max_length=120, null=True, blank=True)
    
    USERNAME_FIELD = 'email'  # Use email for authentication
    REQUIRED_FIELDS = ['username']
    def __str__(self):
        return self.username  # You can use username or email as the user's string representation


# Create your models here.
class Company(models.Model):
    """
    They can't change the company name directly, they have to contact us to change the company name.
    If all the user accounts in a company deleted, the company will also be deleted.
    We will make the deleted = True to every record. this is an another option to keep the records for atleast 6 months.
    We need to notify the last user, if user account is going to be deleted, the company details will be deleted.
    If a user tries to register using a company and if the company details were already there, he needs to contact us.
    There are two ways: 1. he needs to contact us. we will add him manually. this is risky process because we need to change the database.
    2. we need to give him option to add his account by bypassing the verification, only for him spcifically. In this way we don't touch the actual database.
    3. If he chooses, he will be the main account from now on, then we will attach the old company record.
    In any case, if users were not there for the company, it will have to be deleted definitely.
    If, in case, if the customer want to re open the account in 3 months. With in 3 months, if anybody tries to create a new account
    Deletion of Company:
    
    If all user accounts in a company are deleted, delete the company model after a certain period (e.g., 3 months).
    User Notification:
    Notify the last user when their account is going to be deleted, informing them that the associated company details will also be deleted.
    Manual Addition of Users:
    Provide the option for a user to contact you for manual addition if they want to re-open an account within 3 months.
    User Registration with Existing Company:
    If a user tries to register using a company, and the company details already exist, consider these options:
    a. Bypass Verification for the User:
    - Provide an option for the user to register by bypassing the usual verification, specifically for them.
    b. User Becomes Main Account:
    - If the user chooses, make them the main account, attaching the old company record.
    Company Existence Check:
    If someone attempts to register with a company within 3 months of the last user deletion, and the company already exists:
    a. Encourage New Company Registration:
    - Suggest the user register with a new company name.
    Reopening Account After 3 Months:
    If a customer wants to reopen the account after 3 months:
    a. New Company Registration:
    - Encourage them to register with a new company name.
        
    """
    
    name = models.CharField(max_length=300, unique=True)
    sub_domain_name = models.CharField(max_length=1000, unique=True)
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    history = HistoricalRecords()
    created_by = models.ForeignKey(User, related_name='company_model_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='company_model_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.sub_domain_name}"

    class Meta:
        unique_together = ['name', 'sub_domain_name']


    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(Company, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user


class CustomerCompanyDetails(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    company_root_user = models.ForeignKey(User, related_name="company_root_user", on_delete=models.SET_NULL, null=True, blank=True) # contributor
    company_user = models.ForeignKey(User, related_name="company_user", on_delete=models.SET_NULL, null=True, blank=True) # collaborator
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    history = HistoricalRecords()
    created_by = models.ForeignKey(User, related_name='company_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='company_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        if self.company_user != None:
            current_user = 'Collaborator'
            current_user_name = self.company_user.username
        if self.company_root_user != None:
            current_user = 'Contributor'
            current_user_name = self.company_root_user.username
        return_string = current_user_name + ' is a ' + current_user + ' for ' + self.company.name + ' company and space is ' + self.company.sub_domain_name
        return return_string

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(CustomerCompanyDetails, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
