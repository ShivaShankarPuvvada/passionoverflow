from django.utils.translation import gettext_lazy as _

from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.auth import get_user_model
from tags import models as tag_models
from stages import models as stage_models
from segments import models as segment_models
from accounts import models as account_models

User = get_user_model()

# Create your models here.
class Ticket(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "1", _("Active tickets represent tickets or issues that are currently being worked on, are in progress, or are actively being addressed by team members.")
        INACTIVE = "2", _("Inactive tickets represent tickets or issues that are not currently being worked on, have been completed, or have been put on hold for various reasons like, a ticket has been postponed, deprioritized, or is awaiting further action.")
        COMPLETED = "3", _("When candidate finishes the task, he can move the ticket to a Finished stage. Completed tickets are the one which was marked as Completed by Any Assigner.")
        ONHOLD = "4", _("When this task or ticket is suddenly not required future or not important or need to do later based on another requirement, On Hold tickets are the one which was marked as On Hold by Any Assigner.")

    class Priority(models.TextChoices):
        HIGH = "1", _("This level is used for tasks or issues that require immediate attention or have a significant impact on the project, business, or customer satisfaction. High-priority items are typically those that need to be resolved or addressed as soon as possible. It's 'good' to use this level for critical issues that genuinely require urgent action.")
        MEDIUM = "2", _("Medium-priority items are important but not as urgent as high-priority tasks. They might have a significant impact if not addressed promptly but don't require immediate attention. These are often used for tasks or issues that need to be addressed in the near future but can wait for a short period. It's 'good' to use this level for important tasks that need to be scheduled and managed carefully.")
        LOW = "3", _("Low-priority items are not time-sensitive and can be addressed at a later date without significant negative consequences. These are often used for tasks or issues that are nice-to-have but not critical for the current phase of a project or operation. It's 'good' to use this level for non-urgent, lower-impact items that can be deprioritized when higher-priority tasks emerge.")

    class PriorityScale(models.TextChoices):
        TEN = "10", _("High")
        NINE = "09", _("High")
        EIGHT = "08", _("High")
        SEVEN = "07", _("High")
        SIX = "06", _("MEDIUM")
        FIVE = "05", _("MEDIUM")
        FOUR = "04", _("MEDIUM")
        THREE = "03", _("LOW")
        TWO = "02", _("LOW")
        ONE = "01", _("LOW")

    class PriorityType(models.TextChoices):
        TEXTOPTION = "1", _("Text Option allows to select priority using High, Medium and Low for a ticket.")
        SCALEOPTION = "2", _("Scale Option allows to select priority using 1 to 10 for a ticket.")

    class TicketType(models.TextChoices):
        BUG = "01", _("A Bug is a flaw or error in a computer program that causes it to behave in an unintended or unexpected way. A bug has to be resolved.")
        FEATURE = "02", _("A Feature is a new block that has to be implemented based on a idea.")
        ENHANCEMENT = "03", _("If you want to add more or update something, Enhancement is the one to choose.")
        USERSTORY = "04", _("If you're using Agile methodologies like Scrum, you might use this to describe user requirements. User stories focus on delivering value to the end-user.")
        TECHNICALDEBT = "05", _("This category can be used to track tasks related to code refactoring, code quality improvements, and addressing technical issues that may not be visible to end-users but need attention. Make sure to add all the necessary sub tickets and super tickets.")
        DOCUMENTATION = "06", _("Tasks related to creating or updating documentation, including user manuals, API documentation, or internal documentation.")
        RESEARCH = "07", _("For tasks that involve investigating new technologies, evaluating potential solutions, or conducting market research.")
        DEPLOYMENT = "08", _("Tasks related to deploying code to production, configuring servers, or managing deployment pipelines.")
        TESTING = "09", _("Tasks related to quality assurance and testing efforts, including test case creation, test execution, and bug verification.")
        SUPPORT = "10", _("If your project involves ongoing support for end-users, you can use this category to track support requests and issues.")
        SECURITY = "11", _("Tasks related to identifying and addressing security vulnerabilities or implementing security features.")
        INFRASTRUCTURE = "12", _("For tasks related to server maintenance, cloud infrastructure management, or network configuration.")
        COMPLIANCE = "13", _("If your project must adhere to specific regulations or compliance standards, you can use this category to track tasks related to compliance efforts.")
        DATA = "14", _("Tasks related to data management, data migration, or database schema changes.")
        PERFORMANCE = "15", _("Tasks focused on optimizing system performance, including profiling, benchmarking, and optimization efforts.")
        USABILITY = "16", _("Tasks related to improving the overall user experience, including user interface design and usability testing.")
        LOCALIZATION = "17", _("If your project is available in multiple languages, you can use this category for tasks related to translation and localization.")
        TRAINING = "18", _("Tasks related to training team members or end-users on how to use the software or tools effectively.")

    class Deleted(models.TextChoices):
        YES = '1', _("This ticket was deleted by user.")
        NO = '2', _("This tickect was not deleted by user.")

    super_tickets = models.ManyToManyField('self', related_name='tickets_super_tickets', blank=True, symmetrical=False) # All super tickets that this ticket is a part of. I.e, if this ticket is a dependency for any other tickets, we need to add all such other tickets in this field.
    sub_tickets = models.ManyToManyField('self', related_name='tickets_sub_tickets', blank=True, symmetrical=False) # All sub tickets.
    title = models.CharField(max_length=200) # A short, descriptive title for the ticket.
    description = models.TextField(blank=True, null=True) # A more detailed description of the ticket.
    start_date = models.DateField() # The date when work on the ticket should start.
    end_date = models.DateField() # The date when the ticket was completed or resolved.
    estimated_end_date = models.DateField() # An approximated estimation date and time required to complete the ticket.
    due_date = models.DateField() # The specific deadline date by which the ticket should be completed.
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.ACTIVE)
    priority_type = models.CharField(max_length=1, choices=PriorityType.choices, default=PriorityType.TEXTOPTION)
    priority = models.CharField(max_length=1, choices=Priority.choices, default=Priority.MEDIUM)
    priority_scale = models.CharField(max_length=2, choices=PriorityScale.choices, default=PriorityScale.ONE)
    ticket_type = models.CharField(max_length=2, choices=TicketType.choices, default=TicketType.FEATURE)
    deleted = models.CharField(max_length=1, choices=Deleted.choices, default=Deleted.NO) # we will keep the user deleted tickets as well.
    segment = models.ForeignKey(segment_models.Segment, related_name='ticket_segment', on_delete=models.SET_NULL, null=True, blank=True) # segment is a sub part of the project. this field represents that this ticket belongs to which segment.
    assigned_by = models.ManyToManyField(User, related_name='ticket_assigned_by', blank=True) # anybody can assign task to anybody if they have proper permissions.
    assigned_to = models.ManyToManyField(User, related_name='ticket_assigned_to', blank=True) # anybody can get ticket assigned. if they are not present in database, an invitation has to be sent to their company mail.
    members = models.ManyToManyField(User, related_name='ticket_members', blank=True) # represent all members belongs to this ticket. Note that we exclude the members of sub and super tickets.
    tags = models.ManyToManyField(tag_models.Tag, related_name='ticket_tags', blank=True) # tags might be skills, teams, project names etc.., Basically what the user want to categorize, for the search purpose.
    stages = models.ManyToManyField(stage_models.Stage, through='TicketStage') # at which stage the ticket is in. For ex: Newly Created, Assigned, Blocked or On Hold, In progress, Testing, Review, Approval, Completed, Closed, Reopened and Canceled.
    history = HistoricalRecords() # this field will store all the updations done to this model so far.
    company_ticket_counter = models.PositiveIntegerField(default=1) # this is the number of tickets used for a company. This is the actual ticket id. This is unique for each company per each ticket. Two companies can have the same ticket number.
    created_by = models.ForeignKey(User, related_name='ticket_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='ticket_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Generate a unique ticket ID based on the company's identifier
            self.company_ticket_counter = self.generate_unique_ticket_counter()
        super().save(*args, **kwargs)

    def generate_unique_ticket_counter(self):
        company_details = account_models.CustomerCompanyDetails.objects.filter(company_user=self.created_by).latest()
        # Retrieve the last used counter for this company and increment it
        last_ticket = Ticket.objects.filter(segment__project__company=company_details).order_by('-company_ticket_counter').first()
        if last_ticket:
            return last_ticket.company_ticket_counter + 1
        else:
            return 1

    def __str__(self):
        return f"#{self.company_ticket_counter}"
    
class TicketStage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    stage = models.ForeignKey(stage_models.Stage, on_delete=models.CASCADE)


# updated_by is not required for this model because on who creates only able to update.
class Post(models.Model):
    class Deleted(models.TextChoices):
        YES = '1', _("This post was deleted by user.")
        NO = '2', _("This post was not deleted by user.")
        
    ticket = models.ForeignKey(Ticket, related_name='post_ticket', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField() # this is the actual field that will store the data. On React Js side, we have to use the CKEditor. We don't need to use the CKEditor in django. The text field is enough to save the CKEditor RichTextData from React JS.
    history = HistoricalRecords() # this field will store all the updations done to this model so far.
    deleted = models.CharField(max_length=1, choices=Deleted.choices, default=Deleted.NO) # we will keep the user deleted tickets as well.
    created_by = models.ForeignKey(User, related_name='post_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Post by @{self.created_by.username} on Ticket #{self.ticket.id}'
    

class SavedPost(models.Model):
    class Saved(models.TextChoices):
        YES = '1', _("This post was saved by user.")
        NO = '2', _("This post was not saved by user.")
    post = models.ForeignKey(Post, related_name='saved_posts', on_delete=models.SET_NULL, null=True, blank=True)
    saved_by = models.ForeignKey(User, related_name='post_saved_by', on_delete=models.SET_NULL, null=True, blank=True)
    saved = models.CharField(max_length=1, choices=Saved.choices, default=Saved.NO) # we will keep the user saved and unsaved posts as well.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'post - {self.post.id} saved by @{self.created_by.username}'