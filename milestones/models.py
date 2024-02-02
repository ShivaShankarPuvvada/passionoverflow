from django.db import models

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

Project milestones are significant points in a project timeline that represent achievements or completion of specific tasks. Defining and tracking milestones is crucial for project management as they provide a roadmap for the project team and stakeholders, helping ensure that the project stays on track and meets its objectives. The choice of models for project milestones can vary depending on the nature of the project and the industry. Here are some common models for project milestones:

Timeline-Based Milestones:
Project Kickoff: The official start of the project, often marked by a kickoff meeting.
Completion of Project Planning: Milestone when all project planning activities, such as defining scope, creating a project plan, and setting up resources, are completed.
Major Phase Completion: Milestones for completing major phases or stages of the project, such as design, development, testing, and deployment.
Deliverable-Based Milestones:
Requirements Document Approved: Milestone indicating the approval of the project's requirements document.
Prototype Completion: Milestone for completing the development of a prototype or proof of concept.
Software Release: Milestone representing the release of a software version or product iteration.
Client Approval Milestones:
Client Review and Approval: Milestones for obtaining client or stakeholder approval at key points in the project, ensuring alignment with expectations.
User Acceptance Testing (UAT) Approval: Milestone indicating successful completion of user acceptance testing and client approval for deployment.
Budget and Resource Milestones:
Budget Approval: Milestone marking the approval of the project budget.
Resource Allocation: Milestone representing the allocation of necessary resources to the project, including personnel, equipment, and funding.
Risk Management Milestones:
Risk Assessment and Mitigation: Milestone for completing the identification and assessment of project risks, along with the implementation of mitigation strategies.
Issue Resolution: Milestone indicating the successful resolution of critical project issues.
Regulatory Compliance Milestones:
Regulatory Approvals Obtained: Milestone representing the achievement of necessary regulatory approvals for the project.
Training and Knowledge Transfer:
Training Completion: Milestone for completing training sessions for project team members or end-users.
Knowledge Transfer: Milestone representing the successful transfer of knowledge within the project team.
Quality Assurance and Testing:
Test Plan Approval: Milestone indicating the approval of the project's test plan.
Test Completion: Milestone for completing all testing activities, including unit testing, integration testing, and system testing.
Infrastructure Setup and Configuration:
Environment Setup: Milestone representing the completion of the necessary infrastructure and environment setup for development, testing, and deployment.
Go-Live and Post-Implementation:
Go-Live: Milestone for the official launch or deployment of the project.
Post-Implementation Review: Milestone for conducting a review after deployment to evaluate the project's success and identify areas for improvement.
It's important to customize milestone models based on the specific needs and characteristics of each project. Milestones should be well-defined, measurable, and achievable within a specific timeframe to effectively guide project progress.
"""

# Create your models here.
class Milestone(models.Model):
    title = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=2, default="1")
    company = models.ForeignKey(account_models.Company, on_delete=models.PROTECT)
    completion_date = models.DateField() # A date milestone is achieved.
    phases = models.ManyToManyField(phase_models.Phase, blank=True)
    tickets = models.ManyToManyField(ticket_models.Ticket, blank=True)
    stages = models.ManyToManyField(stage_models.Stage, blank=True)
    sprints = models.ManyToManyField(sprint_models.Sprint, blank=True)
    project = models.ForeignKey(project_models.Project, on_delete=models.CASCADE, related_name='project_milestones', null=True, blank=True) # project specific milestone
    segment = models.ForeignKey(segment_models.Segment, on_delete=models.CASCADE, related_name='segment_milestones', null=True, blank=True) # segment specific milestone
    deleted = models.BooleanField(default=False)  # New field to mark soft-deleted records
    history = HistoricalRecords()
    created_by = models.ForeignKey(User, related_name='milestone_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='milestone_updated_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.title