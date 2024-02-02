from django.utils.translation import gettext_lazy as _

from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.auth import get_user_model
from tags import models as tag_models
from stages import models as stage_models
from segments import models as segment_models
from accounts import models as account_models

User = get_user_model()


"""
    # Users can post the ideas as tickets. 
    # These ideas can be reviewed by anyone who can access the ticket. 
    # The calculation for the ideas will be done by adding their inputs.
    
    # add this field in the models for idea submission and calculation.
    idea_calculation = models.TextField(blank=True, null=True)

    # add these methods to the models for idea submission and calculation.
    def calculate_idea(self):
        # Consider factors for cost reduction
        # You can customize this based on your project and business requirements

        # Example: Calculate idea based on estimated cost savings
        estimated_cost_savings = self.calculate_estimated_cost_savings()

        # Example: Consider impact on productivity
        productivity_impact = self.calculate_productivity_impact()

        # Example: Consider time saved
        time_saved = self.calculate_time_saved()

        # Combine factors into an overall idea calculation
        overall_idea_calculation = f"Estimated Cost Savings: {estimated_cost_savings}, Productivity Impact: {productivity_impact}, Time Saved: {time_saved}"

        # Update the idea_calculation field
        self.idea_calculation = overall_idea_calculation

    def calculate_estimated_cost_savings(self):
        # Your logic for estimating cost savings goes here
        # For example, you might consider reduced resource costs, infrastructure savings, etc.
        return "$100,000"  # Placeholder value, replace with your actual calculation

    def calculate_productivity_impact(self):
        # Your logic for estimating productivity impact goes here
        # For example, you might consider improved efficiency, reduced errors, etc.
        return "High"  # Placeholder value, replace with your actual calculation

    def calculate_time_saved(self):
        # Your logic for estimating time saved goes here
        # For example, you might consider reduced development time, faster processes, etc.
        return "2 weeks"  # Placeholder value, replace with your actual calculation

    def save(self, *args, **kwargs):
        self.calculate_idea()  # Call the calculate_idea method before saving
        super().save(*args, **kwargs)

"""
# Create your models here.
class Ticket(models.Model):
    """
    User can create the ticket in a stage.
    The ticket will be under a particular segment.
    The segment will be under particular project.
    The ticket priority is two types. 
    Priority can be selected segment wise. 
    The one who created the segment should select priority. 
    This should not be changed later.
    """
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
    
    # anybody can assign task to anybody if they have proper permissions.
    assigned_by = models.ManyToManyField(User, through='TicketAssignment', related_name='ticket_assigned_by', through_fields=('ticket', 'assigned_by'), blank=True)
    
    # anybody can get ticket assigned. if they are not present in database, an invitation has to be sent to their company mail.
    assigned_to = models.ManyToManyField(User, through='TicketAssignment', related_name='ticket_assigned_to', through_fields=('ticket', 'assigned_to'), blank=True)

   
    members = models.ManyToManyField(User, related_name='ticket_members', blank=True) # represent all members belongs to this ticket. Note that we exclude the members of sub and super tickets.
    tags = models.ManyToManyField(tag_models.Tag, related_name='ticket_tags', blank=True) # tags might be skills, teams, project names etc.., Basically what the user want to categorize, for the search purpose.
    stages = models.ManyToManyField(stage_models.Stage, through='TicketStage') # at which stage the ticket is in. For ex: Newly Created, Assigned, Blocked or On Hold, In progress, Testing, Review, Approval, Completed, Closed, Reopened and Canceled.
    history = HistoricalRecords() # this field will store all the updations done to this model so far.
    company_ticket_counter = models.PositiveIntegerField(default=1) # this is the number of tickets used for a company. This is the actual ticket id. This is unique for each company per each ticket. Two companies can have the same ticket number.
    created_by = models.ForeignKey(User, related_name='ticket_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='ticket_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Generate a unique ticket ID based on the company's identifier
            self.company_ticket_counter = self.generate_unique_ticket_counter()
        super().save(*args, **kwargs)

    def generate_unique_ticket_counter(self):
        customer_company_details = account_models.CustomerCompanyDetails.objects.filter(company_user=self.created_by).latest()
        # Retrieve the last used counter for this company and increment it
        last_ticket = Ticket.objects.filter(segment__project__company=customer_company_details.company).order_by('-company_ticket_counter').first()
        if last_ticket:
            return last_ticket.company_ticket_counter + 1
        else:
            return 1

    def __str__(self):
        return f"#{self.company_ticket_counter}"
    


class TicketAssignment(models.Model):
    """
    # Example usage in a view or serializer
    ticket_instance = Project.objects.get(pk=1)

    # Historical assignments given by ticket_instance.assigned_by
    assignments_given = ticket_instance.assigned_by.all()

    # Historical assignments received by ticket_instance.assigned_to
    assignments_received = ticket_instance.assigned_to.all()
    
    from .models import Assignment

    # Get the latest assignment for a particular ticket
    latest_assignment = Assignment.objects.filter(ticket=ticket_instance).latest('assigned_at')
    
    from django.core.exceptions import ObjectDoesNotExist

    try:
        latest_assignment = Assignment.objects.filter(ticket=ticket_instance).latest('assigned_at')
    except ObjectDoesNotExist:
        # Handle the case where no assignments exist for the ticket
        latest_assignment = None
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(User, related_name='ticket_assignment_given_by', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(User, related_name='ticket_assignment_received_to', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='ticket_assignment_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='ticket_assignment_updated_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
   
    def __str__(self):
        sentence = "#" + self.ticket.company_ticket_counter
        return sentence
     

class TicketStage(models.Model):
    """
    User can create multiple stages. A ticket can be at only one stage at a time. Stages are vertical boxes at kanban board.
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    stage = models.ForeignKey(stage_models.Stage, on_delete=models.CASCADE)


# updated_by is not required for this model because on who creates only able to update.
class Post(models.Model):
    """
    User can post on ticket detail page. 
    If we click on ticket, we can see the list of posts.
    User who created the ticket can mark the post as accepted solution.
    There should be an option to show solution at the top, if one exists.
    User can reply to any post. The reply will be a other post.
    """
    class Deleted(models.TextChoices):
        YES = '1', _("This post was deleted by user.")
        NO = '2', _("This post was not deleted by user.")
        
    ticket = models.ForeignKey(Ticket, related_name='post_ticket', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField() # this is the actual field that will store the data. On React Js side, we have to use the CKEditor. We don't need to use the CKEditor in django. The text field is enough to save the CKEditor RichTextData from React JS.
    upvotes = models.IntegerField(default=0) # increase the count if upvoted.
    downvotes = models.IntegerField(default=0) # increase the count if downvoted.
    accepted_solution = models.BooleanField(default=False)  # creator of the ticket can check it as accepted solution.
    parent_post = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE) # new post id will be 2 and this field id is 1. User can select any post and create reply as seperate post.
    history = HistoricalRecords() # this field will store all the updations done to this model so far.
    deleted = models.CharField(max_length=1, choices=Deleted.choices, default=Deleted.NO) # we will keep the user deleted tickets as well.
    created_by = models.ForeignKey(User, related_name='post_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'Post by @{self.created_by.username} on Ticket #{self.ticket.id}'
    

class SavedPost(models.Model):
    """
    User can save the post. This is for saving his favourite posts. He can come and check his saved posts later.
    """
    class Saved(models.TextChoices):
        YES = '1', _("This post was saved by user.")
        NO = '2', _("This post was not saved by user.")
    post = models.ForeignKey(Post, related_name='saved_posts', on_delete=models.SET_NULL, null=True, blank=True)
    saved_by = models.ForeignKey(User, related_name='post_saved_by', on_delete=models.SET_NULL, null=True, blank=True)
    saved = models.CharField(max_length=1, choices=Saved.choices, default=Saved.YES) # we will keep the user saved and unsaved posts as well.
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records. this is for developers. When customers delete the record, we don't delete it in our database.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'post - {self.post.id} saved by @{self.saved_by.username}'



class PinnedPost(models.Model):
    """
    User can pin the post.
    All the pinned posts will be shown in top in an order. 
    At the bottom of that, normal posts will be shown in order.
    When user un pin the post, we need to change the 'saved' field to Pinned.NO
    While filtering the Pinned posts we need to inclued saved = YES in the filter.
    """
    class Pinned(models.TextChoices):
        YES = '1', _("This post was pinned by user.")
        NO = '2', _("This post was not pinned by user.")
    post = models.ForeignKey(Post, related_name='pinned_posts', on_delete=models.SET_NULL, null=True, blank=True)
    pinned_by = models.ForeignKey(User, related_name='post_pinned_by', on_delete=models.SET_NULL, null=True, blank=True)
    saved = models.CharField(max_length=1, choices=Pinned.choices, default=Pinned.YES) # we will keep the user pinned and unpinned posts as well. i.e, if he un pins, we will change this to NO.
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records. this is for developers. When customers delete the record, we don't delete it in our database.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'post - {self.post.id} pinned by @{self.saved_by.username}'



class Vote(models.Model):
    """
    User can upvote or downvote the post.
    If user was deleted, his opinion won't delete, he already voted to post. Eventhough he left the company the vote matters.
    If we delete the user, we don't delete his vote.
    If post is deleted, then we delete the vote.
    """
    voted_by = models.ForeignKey(User, related_name='post_voted_by', on_delete=models.SET_NULL, null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    vote_type = models.IntegerField(choices=[(1, 'Upvote'), (-1, 'Downvote')])
    deleted = models.BooleanField(default=False) # New field to mark soft-deleted records. this is for developers. When customers delete the record, we don't delete it in our database.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return f'post - {self.post.id} voted by @{self.voted_by.username}'