from django.utils.translation import gettext_lazy as _

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from accounts import models as account_models
from simple_history.models import HistoricalRecords
from phases import models as phase_models
from tickets import models as ticket_models
from sprints import models as sprint_models
from stages import models as stage_models
from projects import models as project_models
from segments import models as segment_models

User = get_user_model()


"""
Milestone model rules:
1. There should be project specific milestone and segment specific milestone.
2. The two project field and segment field should match. Segment should be in the project.

Project milestones are significant points in a project timeline 
that represent achievements or completion of specific tasks. 
Defining and tracking milestones is crucial for project management 
as they provide a roadmap for the project team and stakeholders, 
helping ensure that the project stays on track and meets its objectives. 
The choice of models for project milestones can vary depending on the nature of the project 
and the industry.
It's important to customize milestone models based on the specific needs 
and characteristics of each project. 
Milestones should be well-defined, measurable, 
and achievable within a specific timeframe to effectively guide project progress.
"""

# Create your models here.

OPEN = '1'
CLOSED = '0'
STATUS_CHOICES = [
    (OPEN, 'Open'),
    (CLOSED, 'Close'),
]

class Milestone(models.Model):
    class MilestoneType(models.TextChoices):
        PROJECT_KICKOFF = "01", _("Project Kickoff")  # The official start of the project, often marked by a kickoff meeting.
        PROJECT_PLANNING = "02", _("Completion of Project Planning")  # Milestone when all project planning activities, such as defining scope, creating a project plan, and setting up resources, are completed.
        MAJOR_PHASE = "03", _("Major Phase Completion")  # Milestones for completing major phases or stages of the project, such as design, development, testing, and deployment.
        REQUIREMENTS_APPROVAL = "04", _("Requirements Document Approved")  # Milestone indicating the approval of the project's requirements document.
        PROTOTYPE_COMPLETION = "05", _("Prototype Completion")  # Milestone for completing the development of a prototype or proof of concept.
        SOFTWARE_RELEASE = "06", _("Software Release")  # Milestone representing the release of a software version or product iteration.
        CLIENT_APPROVAL = "07", _("Client Review and Approval")  # Milestones for obtaining client or stakeholder approval at key points in the project, ensuring alignment with expectations.
        UAT_APPROVAL = "08", _("User Acceptance Testing (UAT) Approval")  # Milestone indicating successful completion of user acceptance testing and client approval for deployment.
        BUDGET_APPROVAL = "09", _("Budget Approval")  # Milestone marking the approval of the project budget.
        RESOURCE_ALLOCATION = "10", _("Resource Allocation")  # Milestone representing the allocation of necessary resources to the project, including personnel, equipment, and funding.
        RISK_ASSESSMENT = "11", _("Risk Assessment and Mitigation")  # Milestone for completing the identification and assessment of project risks, along with the implementation of mitigation strategies.
        ISSUE_RESOLUTION = "12", _("Issue Resolution")  # Milestone indicating the successful resolution of critical project issues.
        REGULATORY_APPROVALS = "13", _("Regulatory Approvals Obtained")  # Milestone representing the achievement of necessary regulatory approvals for the project.
        TRAINING_COMPLETION = "14", _("Training Completion")  # Milestone for completing training sessions for project team members or end-users.
        KNOWLEDGE_TRANSFER = "15", _("Knowledge Transfer")  # Milestone representing the successful transfer of knowledge within the project team.
        TEST_PLAN_APPROVAL = "16", _("Test Plan Approval")  # Milestone indicating the approval of the project's test plan.
        TEST_COMPLETION = "17", _("Test Completion")  # Milestone for completing all testing activities, including unit testing, integration testing, and system testing.
        ENVIRONMENT_SETUP = "18", _("Environment Setup")  # Milestone representing the completion of the necessary infrastructure and environment setup for development, testing, and deployment.
        GO_LIVE = "19", _("Go-Live")  # Milestone for the official launch or deployment of the project.
        POST_IMPLEMENTATION_REVIEW = "20", _("Post-Implementation Review")  # Milestone for conducting a review after deployment to evaluate the project's success and identify areas for improvement.

    title = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=OPEN)
    company = models.ForeignKey(account_models.Company, on_delete=models.PROTECT)
    completion_date = models.DateField() # A date milestone is achieved.
    tickets = models.ManyToManyField(ticket_models.Ticket, through='MilestoneTicket')
    phases = models.ManyToManyField(phase_models.Phase, through='MilestonePhase')
    stages = models.ManyToManyField(stage_models.Stage, through='MilestoneStage')
    sprints = models.ManyToManyField(sprint_models.Sprint, through='MilestoneSprint')
    milestone_type = models.CharField(max_length=2, choices=MilestoneType.choices, default=MilestoneType.PROJECT_KICKOFF)
    project = models.ForeignKey(project_models.Project, on_delete=models.CASCADE, related_name='project_milestones', null=True, blank=True) # project specific milestone
    segment = models.ForeignKey(segment_models.Segment, on_delete=models.CASCADE, related_name='segment_milestones', null=True, blank=True) # segment specific milestone
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    history = HistoricalRecords()
    created_by = models.ForeignKey(User, related_name='milestone_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='milestone_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(Milestone, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(Milestone, self).save()


class MilestoneTicket(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    ticket = models.ForeignKey(ticket_models.Ticket, on_delete=models.CASCADE)

    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='milestoneticket_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='milestoneticket_updated_by', blank=True) # anybody can update the ticket. updated message has to be shown in the posts of ticket.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        object_display_message = "Milestone " + self.milestone.title + " is in " + self.ticket.title + " ticket."
        return object_display_message

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(MilestoneTicket, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(MilestoneTicket, self).save()



class MilestonePhase(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    phase = models.ForeignKey(phase_models.Phase, on_delete=models.CASCADE)

    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='milestonephase_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='milestonephase_updated_by', blank=True) # anybody can update the phase. updated message has to be shown in the posts of phase.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        object_display_message = "Milestone " + self.milestone.title + " is in " + self.phase.title + " phase."
        return object_display_message

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(MilestonePhase, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(MilestonePhase, self).save()



class MilestoneStage(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    stage = models.ForeignKey(stage_models.Stage, on_delete=models.CASCADE)

    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='milestonestage_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='milestonestage_updated_by', blank=True) # anybody can update the stage. updated message has to be shown in the posts of stage.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        object_display_message = "Milestone " + self.milestone.title + " is in " + self.stage.title + " stage."
        return object_display_message

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(MilestoneStage, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(MilestoneStage, self).save()



class MilestoneSprint(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    sprint = models.ForeignKey(sprint_models.Sprint, on_delete=models.CASCADE)

    history = HistoricalRecords()
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    created_by = models.ForeignKey(User, related_name='milestonesprint_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ManyToManyField(User, related_name='milestonesprint_updated_by', blank=True) # anybody can update the sprint. updated message has to be shown in the posts of sprint.
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        object_display_message = "Milestone " + self.milestone.title + " is in " + self.sprint.title + " sprint."
        return object_display_message

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_new = not self.pk  # Check if it's a new object creation

        super(MilestoneSprint, self).save(*args, **kwargs)

        if user:
            self.updated_by.add(user)
            if is_new:
                self.created_by = user
                super(MilestoneSprint, self).save()
