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
    Based on typical project management practices, the fields related to the timing of a ticket in your Ticket model can be interpreted as follows:

Start Date (start_date):

This field indicates when work on the ticket is scheduled or intended to begin. It signifies the commencement date of activities related to addressing the ticket.
End Date (end_date):

The end_date field represents the date when the ticket was completed or resolved. It marks the completion date of all work and deliverables associated with the ticket.
Estimated End Date (estimated_end_date):

This field provides an approximate estimation of when the ticket is expected to be completed. It serves as a forecast or prediction of when the ticket might realistically reach its end_date.
Due Date (due_date):

The due_date field specifies the deadline by which the ticket should ideally be completed. It sets the target date for completing the ticket's work to ensure it aligns with project timelines and commitments.
Usage and Interpretation:
Start Date: It helps stakeholders and team members understand when work on the ticket is scheduled to commence. It's often used to track the beginning of efforts related to addressing the ticket's requirements.

End Date: This marks the point in time when all tasks and objectives associated with the ticket are completed. It reflects the actual completion date of the ticket's activities.

Estimated End Date: Provides a projection of when the ticket is anticipated to reach completion. It aids in planning and managing resources and expectations around the ticket's progress.

Due Date: Sets a deadline for the ticket's completion. It helps in prioritizing work and ensuring timely delivery of ticket-related outcomes.

General Workflow:
Start Date and Due Date: Together, these fields define the time window within which the ticket should be worked on and completed.

End Date and Estimated End Date: The end_date reflects the actual completion date once the ticket's work is finished. The estimated_end_date serves as an early projection of when this completion might occur, providing an ongoing forecast of progress.

Implementation Considerations:
Ensure these fields are updated accurately throughout the ticket's lifecycle to reflect the current state and progress.
Utilize Django model methods or signals to automate updates or calculations related to these dates based on ticket status changes or other triggers.
Display these dates prominently in your application's UI to keep stakeholders informed about the ticket's timing and progress.
By incorporating these fields into your Ticket model and managing them effectively, you can enhance transparency, planning, and tracking of ticket-related activities within your project management system. Adjust the interpretation and usage based on specific project requirements and workflows.






    """
    class Status(models.TextChoices):
        ACTIVE = "1", _("Active") #, _("Active tickets represent tickets or issues that are currently being worked on, are in progress, or are actively being addressed by team members.")
        INACTIVE = "2", _("Inactive") # , _("Inactive tickets represent tickets or issues that are not currently being worked on, have been completed, or have been put on hold for various reasons like, a ticket has been postponed, deprioritized, or is awaiting further action.")
        COMPLETED = "3", _("Completed") # , _("When candidate finishes the task, he can move the ticket to a Finished stage. Completed tickets are the one which was marked as Completed by Any Assigner.")
        ONHOLD = "4", _("On Hold") #, _("When this task or ticket is suddenly not required future or not important or need to do later based on another requirement, On Hold tickets are the one which was marked as On Hold by Any Assigner.")

    # class Priority(models.TextChoices):
    #     HIGH = "1", _("This level is used for tasks or issues that require immediate attention or have a significant impact on the project, business, or customer satisfaction. High-priority items are typically those that need to be resolved or addressed as soon as possible. It's 'good' to use this level for critical issues that genuinely require urgent action.")
    #     MEDIUM = "2", _("Medium-priority items are important but not as urgent as high-priority tasks. They might have a significant impact if not addressed promptly but don't require immediate attention. These are often used for tasks or issues that need to be addressed in the near future but can wait for a short period. It's 'good' to use this level for important tasks that need to be scheduled and managed carefully.")
    #     LOW = "3", _("Low-priority items are not time-sensitive and can be addressed at a later date without significant negative consequences. These are often used for tasks or issues that are nice-to-have but not critical for the current phase of a project or operation. It's 'good' to use this level for non-urgent, lower-impact items that can be deprioritized when higher-priority tasks emerge.")

    class PriorityScale(models.TextChoices):
        TEN = "10", _("10")
        NINE = "09", _("9")
        EIGHT = "08", _("8")
        SEVEN = "07", _("7")
        SIX = "06", _("6")
        FIVE = "05", _("5")
        FOUR = "04", _("4")
        THREE = "03", _("3")
        TWO = "02", _("2")
        ONE = "01", _("1")

    # class PriorityType(models.TextChoices):
    #     TEXTOPTION = "1", _("Text Option allows to select priority using High, Medium and Low for a ticket.")
    #     SCALEOPTION = "2", _("Scale Option allows to select priority using 1 to 10 for a ticket.")
    class TicketType(models.TextChoices):
        BUG = "01", _("Bug") # , _("A Bug is a flaw or error in a computer program that causes it to behave in an unintended or unexpected way. A bug has to be resolved.")
        FEATURE = "02", _("Feature") # , _("A Feature is a new block that has to be implemented based on an idea.")
        ENHANCEMENT = "03", _("Enhancement") # , _("If you want to add more or update something, Enhancement is the one to choose.")
        USERSTORY = "04", _("User Story") # , _("If you're using Agile methodologies like Scrum, you might use this to describe user requirements. User stories focus on delivering value to the end-user.")
        TECHNICALDEBT = "05", _("Technical Debt") # , _("This category can be used to track tasks related to code refactoring, code quality improvements, and addressing technical issues that may not be visible to end-users but need attention. Make sure to add all the necessary sub tickets and super tickets.")
        DOCUMENTATION = "06", _("Documentation") # , _("Tasks related to creating or updating documentation, including user manuals, API documentation, or internal documentation.")
        RESEARCH = "07", _("Research") # , _("For tasks that involve investigating new technologies, evaluating potential solutions, or conducting market research.")
        DEPLOYMENT = "08", _("Deployment") # , _("Tasks related to deploying code to production, configuring servers, or managing deployment pipelines.")
        TESTING = "09", _("Testing") # , _("Tasks related to quality assurance and testing efforts, including test case creation, test execution, and bug verification.")
        SUPPORT = "10", _("Support") # , _("If your project involves ongoing support for end-users, you can use this category to track support requests and issues.")
        SECURITY = "11", _("Security") # , _("Tasks related to identifying and addressing security vulnerabilities or implementing security features.")
        INFRASTRUCTURE = "12", _("Infrastructure") # , _("For tasks related to server maintenance, cloud infrastructure management, or network configuration.")
        COMPLIANCE = "13", _("Compliance") # , _("If your project must adhere to specific regulations or compliance standards, you can use this category to track tasks related to compliance efforts.")
        DATA = "14", _("Data") # , _("Tasks related to data management, data migration, or database schema changes.")
        PERFORMANCE = "15", _("Performance") # , _("Tasks focused on optimizing system performance, including profiling, benchmarking, and optimization efforts.")
        USABILITY = "16", _("Usability") # , _("Tasks related to improving the overall user experience, including user interface design and usability testing.")
        LOCALIZATION = "17", _("Localization") # , _("If your project is available in multiple languages, you can use this category for tasks related to translation and localization.")
        TRAINING = "18", _("Training") # , _("Tasks related to training team members or end-users on how to use the software or tools effectively.")

    class Deleted(models.TextChoices):
        YES = '1', _("This ticket was deleted by user.")
        NO = '2', _("This ticket was not deleted by user.")

    super_tickets = models.ManyToManyField('self', related_name='tickets_super_tickets', blank=True, symmetrical=False) # All super tickets that this ticket is a part of. I.e, if this ticket is a dependency for any other tickets, we need to add all such other tickets in this field.
    sub_tickets = models.ManyToManyField('self', related_name='tickets_sub_tickets', blank=True, symmetrical=False) # All sub tickets.
    title = models.CharField(max_length=200) # A short, descriptive title for the ticket.
    description = models.TextField(blank=True, null=True) # A more detailed description of the ticket.
    start_date = models.DateField(blank=True, null=True) # The date when work on the ticket should start.
    end_date = models.DateField(blank=True, null=True) # The date when the ticket was completed or resolved.
    estimated_end_date = models.DateField(blank=True, null=True) # An approximated estimation date and time required to complete the ticket.
    due_date = models.DateField(blank=True, null=True) # The specific deadline date by which the ticket should be completed.
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.ACTIVE)
    # priority_type = models.CharField(max_length=1, choices=PriorityType.choices, default=PriorityType.TEXTOPTION)
    # priority = models.CharField(max_length=1, choices=Priority.choices, default=Priority.MEDIUM)
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
    history = HistoricalRecords() # this field will store all the updates done to this model so far.
    company_ticket_counter = models.PositiveIntegerField(default=1) # this is the number of tickets used for a company. This is the actual ticket id. This is unique for each company per each ticket. Two companies can have the same ticket number.
    created_by = models.ForeignKey(User, related_name='ticket_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='ticket_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def generate_unique_ticket_counter(self):
        contributor = account_models.CustomerCompanyDetails.objects.filter(company_root_user=self.created_by).order_by('-id')
        collaborator = account_models.CustomerCompanyDetails.objects.filter(company_user=self.created_by).order_by('-id')
        if contributor.exists():
            company = contributor.first().company
        elif collaborator.exists():
            company = collaborator.first().company
        # Retrieve the last used counter for this company and increment it
        last_ticket = Ticket.objects.filter(segment__project__company=company).order_by('-company_ticket_counter').first()
        if last_ticket:
            return last_ticket.company_ticket_counter + 1
        else:
            return 1

    def __str__(self):
        return f"#{self.company_ticket_counter}"

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation
        super(Ticket, self).save(*args, **kwargs)
        if user:
            self.updated_by.add(user)
            if is_new:
                # Generate a unique ticket ID based on the company's identifier
                self.created_by = user
                self.company_ticket_counter = self.generate_unique_ticket_counter()
                super(Ticket, self).save()  # Save again to update with generated counter


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
    updated_by = models.ManyToManyField(User, related_name='ticket_assignment_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        sentence = "#" + self.ticket.company_ticket_counter
        return sentence

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(TicketAssignment, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(TicketAssignment, self).save()


class TicketStage(models.Model):
    """
    User can create multiple stages. A ticket can be at only one stage at a time. Stages are vertical boxes at kanban board.
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    stage = models.ForeignKey(stage_models.Stage, on_delete=models.CASCADE)
    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='ticket_stage_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='ticket_stage_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        sentence = "This ticket " + self.ticket.title + "is in this stage " + self.stage.title + "."
        return sentence
    
    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(TicketStage, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(TicketStage, self).save()
