from django.db import models
from django.contrib.auth import get_user_model

from django.utils import timezone
from projects.models import Project
from segments.models import Segment

User = get_user_model()


class Invitation(models.Model):
    """
    A Contributor/admin can invite the collaborators/employees to a project or segment with read or complete acess options.
    Title is for naming his invitations.
    Description is for reasons for him to explain the invitations. He can mention any other Contributors using @ mentions.
    There should be no option for customer to delete any Invitations.
    The Contributor can add access two types: 
    one is by sending mail if he is not a current registered user. He will register by clicking link on the registration link.
    Second one is by giving acess by selecting his mail id. assuming the user is already registered, he will get a mail notification. He can acesss the projects in my projects.
    The Contributor can add access to the user to a project or multiple projects.
    The Contributor can add access to the user to a segment or multiple segments.
    The Contributor can give read only access.
    The Contributor can give write only access.
    If the contributor changes the invitation read_only mode or tries to add or remove the existing record, we will make the old record status to 0 and create a new record.
    We need to always get the records with status 1.
    When segment is changed to another project, we need to make sure we get current project details only.
    """
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=2, default="1")
    read_only = models.BooleanField(default=True)
    expiration_date = models.DateTimeField()
    created_by = models.ForeignKey(User, related_name='invitation_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='invitation_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


    def has_expired(self):
        return timezone.now() > self.expiration_date
    
    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(Invitation, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(Invitation, self).save()

