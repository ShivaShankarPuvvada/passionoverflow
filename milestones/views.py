from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from .models import Milestone, MilestoneTicket, MilestonePhase, MilestoneStage, MilestoneSprint, STATUS_CHOICES, OPEN
from accounts.models import CustomerCompanyDetails, Company
from phases.models import Phase
from tickets.models import Ticket
from stages.models import Stage
from sprints.models import Sprint
from segments.models import Segment
from projects.models import Project
from accounts.views import User
from http import HTTPStatus
import json


@login_required
def create_milestone(request):
    if request.method == 'POST':
        tickets, phases, stages, sprints = [], [], [], []
        try:
            data = request.POST
            # required_fields = ['title', 'completion_date', 'status', 'tickets', 'phases', 'stages', 'sprints', 'milestone_type', 'project_id', 'segment_id']
            required_fields = ['title', 'completion_date']
            # Check for missing required fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'success': False, 'errors': f'Missing fields: {", ".join(missing_fields)}'}, status=HTTPStatus.BAD_REQUEST)

            if 'title' in data:
                title = data['title']
            if 'completion_date' in data:
                completion_date = data.get('completion_date')
            if 'status' in data:
                status = data.get('status', OPEN)  # Default to OPEN if not provided
            if 'tickets' in data:
                tickets = data.getlist('tickets')  # Assuming tickets are received as a list of IDs
            if 'phases' in data:
                phases = data.getlist('phases')  # Assuming phases are received as a list of IDs
            if 'stages' in data:
                stages = data.getlist('stages')  # Assuming stages are received as a list of IDs
            if 'sprints' in data:
                sprints = data.getlist('sprints')  # Assuming sprints are received as a list of IDs
            if 'milestone_type' in data:
                milestone_type = data.get('milestone_type', Milestone.MilestoneType.PROJECT_KICKOFF)  # Default is project kick off
            if 'project_id' in data:
                project_id = data.get('project_id')
            if 'segment_id' in data:
                segment_id = data.get('segment_id')

            # Basic validation
            errors = []
            if not title:
                errors.append("Title is required.")
            if not completion_date:
                errors.append("Completion date is required.")
            if not status:
                errors.append("Status is required.")
            if not isinstance(tickets, list):
                errors.append("Tickets must be a list.")
            if not isinstance(phases, list):
                errors.append("Phases must be a list.")
            if not isinstance(stages, list):
                errors.append("Stages must be a list.")
            if not isinstance(sprints, list):
                errors.append("Sprints must be a list.")
            if not milestone_type:
                errors.append("Milestone type is required.")
            if not project_id:
                errors.append("Project is required.")
            if not segment_id:
                errors.append("Segment is required.")
            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

            with transaction.atomic():
                # Getting company
                company = CustomerCompanyDetails.objects.filter(company_root_user=request.user).first().company

                milestone = Milestone()
                milestone.title=title
                milestone.company=company
                milestone.completion_date=completion_date
                milestone.status=status
                milestone.milestone_type=milestone_type
                
                if project_id:
                    project_objects = Project.objects.filter(id=project_id)
                    if project_objects.exists():
                        milestone.project = project_objects.first()
                
                if segment_id:
                    segment_objects = Segment.objects.filter(id=segment_id)
                    if segment_objects.exists():
                        segment_object = segment_objects.first()
                        if str(segment_object.project.id) == str(project_id): # checking if segment is in the given project id. In template we will only select the 
                            milestone.segment = segment_object
                        else:
                            errors.append("Segment should be in the selected Project.")
                            return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

                milestone.save(user=request.user)

                # Create related MilestoneTicket records
                for ticket_id in tickets:
                    each_ticket = Ticket.objects.filter(id=ticket_id).first()
                    if each_ticket:
                        MilestoneTicket.objects.create(milestone=milestone, ticket=each_ticket)

                # Create related MilestonePhase records
                for phase_id in phases:
                    each_phase = Phase.objects.filter(id=phase_id).first()
                    if each_phase:
                        MilestonePhase.objects.create(milestone=milestone, phase=each_phase)
                
                # Create related MilestoneStage records
                for stage_id in stages:
                    each_stage = Stage.objects.filter(id=stage_id).first()
                    if each_stage:
                        MilestoneStage.objects.create(milestone=milestone, stage=each_stage)

                # Create related MilestoneSprint records
                for sprint_id in sprints:
                    each_sprint = Sprint.objects.filter(id=sprint_id).first()
                    if each_sprint:
                        MilestoneSprint.objects.create(milestone=milestone, sprint=each_sprint)

            return redirect('milestones:milestone_list')

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': ["Invalid JSON data."]}, status=HTTPStatus.BAD_REQUEST)

        except IntegrityError as integrity_error:
            return JsonResponse({'success': False, 'errors': ["Integrity Error: " + str(integrity_error)]}, status=HTTPStatus.BAD_REQUEST)

        except Exception as error:
            print(error)
            return JsonResponse({'success': False, 'errors': ["An unexpected error occurred. Please try again."]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    elif request.method == 'GET':
        status_choices = STATUS_CHOICES
        milestone_type = Milestone.MilestoneType.choices
        user = User.objects.get(pk=request.user.id)
        company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
        tickets = Ticket.objects.filter(segment__project__company=company)
        phases = Phase.objects.filter(company=company)
        stages = Stage.objects.filter(company=company)
        sprints = Sprint.objects.filter(company=company)
        projects = Project.objects.filter(company=company)
        segments = Segment.objects.filter(project__company=company)

        context = {
                    'status_choices': status_choices,
                    'milestone_type': milestone_type,
                    'tickets': tickets, 
                    'phases': phases, 
                    'stages': stages,
                    'sprints': sprints, 
                    'projects': projects,
                    'segments': segments,
                }
        return render(request=request, template_name='milestones/create_milestone.html', context=context)


@login_required
def update_milestone(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    if request.method == 'POST':
        tickets, phases, stages, sprints = [], [], [], []
        try:
            data = request.POST
            # required_fields = ['title', 'completion_date', 'status', 'tickets', 'phases', 'stages', 'sprints', 'milestone_type', 'project_id', 'segment_id']
            required_fields = ['title', 'completion_date']
            # Check for missing required fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'success': False, 'errors': f'Missing fields: {", ".join(missing_fields)}'}, status=HTTPStatus.BAD_REQUEST)

            if 'title' in data:
                title = data['title']
            if 'completion_date' in data:
                completion_date = data.get('completion_date')
            if 'status' in data:
                status = data.get('status', OPEN)  # Default to OPEN if not provided
            if 'tickets' in data:
                tickets = data.getlist('tickets')  # Assuming tickets are received as a list of IDs
            if 'phases' in data:
                phases = data.getlist('phases')  # Assuming phases are received as a list of IDs
            if 'stages' in data:
                stages = data.getlist('stages')  # Assuming stages are received as a list of IDs
            if 'sprints' in data:
                sprints = data.getlist('sprints')  # Assuming sprints are received as a list of IDs
            if 'milestone_type' in data:
                milestone_type = data.get('milestone_type', Milestone.MilestoneType.PROJECT_KICKOFF)  # Default is project kick off
            if 'project_id' in data:
                project_id = data.get('project_id')
            if 'segment_id' in data:
                segment_id = data.get('segment_id')

            # Basic validation
            errors = []
            if not title:
                errors.append("Title is required.")
            if not completion_date:
                errors.append("Completion date is required.")
            if not status:
                errors.append("Status is required.")
            if not isinstance(tickets, list):
                errors.append("Tickets must be a list.")
            if not isinstance(phases, list):
                errors.append("Phases must be a list.")
            if not isinstance(stages, list):
                errors.append("Stages must be a list.")
            if not isinstance(sprints, list):
                errors.append("Sprints must be a list.")
            if not milestone_type:
                errors.append("Milestone type is required.")
            if not project_id:
                errors.append("Project is required.")
            if not segment_id:
                errors.append("Segment is required.")
            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

            with transaction.atomic():
                # Getting company
                company = CustomerCompanyDetails.objects.filter(company_root_user=request.user).first().company

                milestone.title=title
                milestone.company=company
                milestone.completion_date=completion_date
                milestone.status=status
                milestone.milestone_type=milestone_type
                
                if project_id:
                    project_objects = Project.objects.filter(id=project_id)
                    if project_objects.exists():
                        milestone.project = project_objects.first()
                
                if segment_id:
                    segment_objects = Segment.objects.filter(id=segment_id)
                    if segment_objects.exists():
                        segment_object = segment_objects.first()
                        if str(segment_object.project.id) == str(project_id): # checking if segment is in the given project id. In template we will only select the 
                            milestone.segment = segment_object
                        else:
                            errors.append("Segment should be in the selected Project.")
                            return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

                milestone.save(user=request.user)


                # Update MilestoneTicket model
                current_tickets = milestone.tickets.all()
                current_ticket_ids = set(current_tickets.values_list('id', flat=True))
                new_ticket_ids = set(map(int, tickets))

                tickets_to_add = new_ticket_ids - current_ticket_ids
                tickets_to_remove = current_ticket_ids - new_ticket_ids

                for ticket_id in tickets_to_add:
                    ticket = Ticket.objects.get(id=ticket_id)
                    MilestoneTicket.objects.create(milestone=milestone, ticket=ticket)

                for ticket_id in tickets_to_remove:
                    MilestoneTicket.objects.filter(milestone=milestone, ticket__id=ticket_id).delete()

                # Update MilestonePhase model
                current_phases = milestone.phases.all()
                current_phase_ids = set(current_phases.values_list('id', flat=True))
                new_phase_ids = set(map(int, phases))

                phases_to_add = new_phase_ids - current_phase_ids
                phases_to_remove = current_phase_ids - new_phase_ids

                for phase_id in phases_to_add:
                    phase = Phase.objects.get(id=phase_id)
                    MilestonePhase.objects.create(milestone=milestone, phase=phase)

                for phase_id in phases_to_remove:
                    MilestonePhase.objects.filter(milestone=milestone, phase__id=phase_id).delete()

                # Update MilestoneStage model
                current_stages = milestone.stages.all()
                current_stage_ids = set(current_stages.values_list('id', flat=True))
                new_stage_ids = set(map(int, stages))

                stages_to_add = new_stage_ids - current_stage_ids
                stages_to_remove = current_stage_ids - new_stage_ids

                for stage_id in stages_to_add:
                    stage = Stage.objects.get(id=stage_id)
                    MilestoneStage.objects.create(milestone=milestone, stage=stage)

                for stage_id in stages_to_remove:
                    MilestoneStage.objects.filter(milestone=milestone, stage__id=stage_id).delete()

                # Update MilestoneSprint model
                current_sprints = milestone.sprints.all()
                current_sprint_ids = set(current_sprints.values_list('id', flat=True))
                new_sprint_ids = set(map(int, sprints))

                sprints_to_add = new_sprint_ids - current_sprint_ids
                sprints_to_remove = current_sprint_ids - new_sprint_ids

                for sprint_id in sprints_to_add:
                    sprint = Sprint.objects.get(id=sprint_id)
                    MilestoneSprint.objects.create(milestone=milestone, sprint=sprint)

                for sprint_id in sprints_to_remove:
                    MilestoneSprint.objects.filter(milestone=milestone, sprint__id=sprint_id).delete()

            # redirecting to list if update happened.
            return redirect('milestones:milestone_list')

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': ["Invalid JSON data."]}, status=HTTPStatus.BAD_REQUEST)

        except IntegrityError as integrity_error:
            return JsonResponse({'success': False, 'errors': ["Integrity Error: " + str(integrity_error)]}, status=HTTPStatus.BAD_REQUEST)

        except Exception as error:
            print(error)
            return JsonResponse({'success': False, 'errors': ["An unexpected error occurred. Please try again."]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    elif request.method == 'GET':
        # Prepare context for rendering the update form with the updated milestone
        status_choices = STATUS_CHOICES
        milestone_type = Milestone.MilestoneType.choices
        user = User.objects.get(pk=request.user.id)
        company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
        tickets = Ticket.objects.filter(segment__project__company=company)
        phases = Phase.objects.filter(company=company)
        stages = Stage.objects.filter(company=company)
        sprints = Sprint.objects.filter(company=company)
        projects = Project.objects.filter(company=company)
        segments = Segment.objects.filter(project__company=company)

        context = {
            'milestone': milestone,
            'status_choices': status_choices,
            'milestone_type': milestone_type,
            'tickets': tickets,
            'phases': phases,
            'stages': stages,
            'sprints': sprints,
            'projects': projects,
            'segments': segments,
        }
        return render(request, 'milestones/update_milestone.html', context=context)


@login_required
def get_all_milestones(request):
    user = request.user
    company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
    milestones = Milestone.objects.filter(company=company).order_by('-id')
    
    context = {
        'milestones': milestones
    }
    return render(request, 'milestones/milestone_list.html', context)


# we are not validating segment belongs to the same project currently.
# we are only sending project related segments if project is selected.
# we are only making js select the project automatically if the segment is selected.
def validate_segment_project(request):
    project_id = request.GET.get('project_id')
    segment_id = request.GET.get('segment_id')
    valid = False
    # Your validation logic here
    # Example: Check if segment belongs to the project
    segments = Segment.objects.filter(id=segment_id)
    if segments.exists():
        segment = segments.first()
        if str(segment.project.id) == str(project_id):
            valid = True

    # Return JSON response indicating validation result
    return JsonResponse({'valid': valid})


# this will get project related segments if project selected.
def get_segments_by_project(request):
    project_id = request.GET.get('project_id')
    if project_id:
        segments = Segment.objects.filter(project__id=project_id).values('id', 'title')
        segments_list = list(segments)
        return JsonResponse({'segments': segments_list})
    return JsonResponse({'segments': []})

# this will get project if segment is selected.
def get_project_by_segment(request):
    segment_id = request.GET.get('segment_id')
    segment = Segment.objects.get(id=segment_id)
    project = segment.project
    return JsonResponse({'project': {'id': project.id, 'title': project.title}})


@login_required
def get_all_milestones_in_calendar(request):
    user = request.user
    company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
    milestones = Milestone.objects.filter(company=company).order_by('-id')

    # Initialize an empty list to store milestone data
    milestones_data = []

    # Fetch and process milestones
    for milestone in milestones:
        # Fetch related data
        tickets = milestone.tickets.all()
        phases = milestone.phases.all()
        stages = milestone.stages.all()
        sprints = milestone.sprints.all()
        
        # Prepare milestone data
        data = {
            'id': str(milestone.id),
            'title': milestone.title,
            'status': milestone.get_status_display(),
            'completion_date': milestone.completion_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'milestone_type': milestone.get_milestone_type_display(),
            'project': milestone.project.title if milestone.project else 'None',
            'segment': milestone.segment.title if milestone.segment else 'None',
            'tickets': ', '.join(ticket.title for ticket in tickets),
            'phases': ', '.join(phase.title for phase in phases),
            'stages': ', '.join(stage.title for stage in stages),
            'sprints': ', '.join(sprint.title for sprint in sprints),
        }
        milestones_data.append(data)

    context = {
        'milestones': milestones_data
    }
    return render(request, 'milestones/milestone_calendar.html', context)