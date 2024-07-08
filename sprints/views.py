from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from .models import Sprint, SprintTicket, SprintPhase, SprintSegment, SprintProject, STATUS_CHOICES, OPEN
from accounts.models import CustomerCompanyDetails, Company
from phases.models import Phase
from tickets.models import Ticket
from segments.models import Segment
from projects.models import Project
from accounts.views import User
from http import HTTPStatus
import json


@login_required
def create_sprint(request):
    if request.method == 'POST':
        tickets, phases, segments, projects = [], [], [], []
        try:
            data = request.POST
            # required_fields = ['title', 'start_date', 'end_date', 'status', 'tickets', 'phases', 'segments', 'projects']
            required_fields = ['title', 'start_date', 'end_date']
            # Check for missing required fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'success': False, 'errors': f'Missing fields: {", ".join(missing_fields)}'}, status=HTTPStatus.BAD_REQUEST)

            if 'title' in data:
                title = data['title']
            if 'start_date' in data:
                start_date = data.get('start_date')
            if 'end_date' in data:
                end_date = data.get('end_date')
            if 'status' in data:
                status = data.get('status', OPEN)  # Default to OPEN if not provided
            if 'tickets' in data:
                tickets = data.getlist('tickets')  # Assuming tickets are received as a list of IDs
            if 'phases' in data:
                phases = data.getlist('phases')  # Assuming phases are received as a list of IDs
            if 'segments' in data:
                segments = data.getlist('segments')  # Assuming segments are received as a list of IDs
            if 'projects' in data:
                projects = data.getlist('projects')  # Assuming projects are received as a list of IDs

            # Basic validation
            errors = []
            if not title:
                errors.append("Title is required.")
            if not start_date:
                errors.append("Start date is required.")
            if not end_date:
                errors.append("End date is required.")
            if not status:
                errors.append("Status is required.")
            if not isinstance(tickets, list):
                errors.append("Tickets must be a list.")
            if not isinstance(phases, list):
                errors.append("Phases must be a list.")
            if not isinstance(segments, list):
                errors.append("Segments must be a list.")
            if not isinstance(projects, list):
                errors.append("Projects must be a list.")
            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

            with transaction.atomic():
                # Getting company
                company = CustomerCompanyDetails.objects.filter(company_root_user=request.user).first().company

                sprint = Sprint.objects.create(
                    title=title,
                    company=company,
                    start_date=start_date,
                    end_date=end_date,
                    status=status,
                )

                # Create related SprintPhase records
                for ticket_id in tickets:
                    each_ticket = Ticket.objects.filter(id=ticket_id).first()
                    if each_ticket:
                        SprintTicket.objects.create(sprint=sprint, ticket=each_ticket)

                # Create related SprintPhase records
                for phase_id in phases:
                    each_phase = Phase.objects.filter(id=phase_id).first()
                    if each_phase:
                        SprintPhase.objects.create(sprint=sprint, phase=each_phase)
                
                # Create related SprintPhase records
                for segment_id in segments:
                    each_segment = Segment.objects.filter(id=segment_id).first()
                    if each_segment:
                        SprintSegment.objects.create(sprint=sprint, segment=each_segment)

                # Create related SprintPhase records
                for project_id in projects:
                    each_project = Project.objects.filter(id=project_id).first()
                    if each_project:
                        SprintProject.objects.create(sprint=sprint, project=each_project)

            return redirect('sprints:sprint_list')

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': ["Invalid JSON data."]}, status=HTTPStatus.BAD_REQUEST)

        except IntegrityError as integrity_error:
            return JsonResponse({'success': False, 'errors': ["Integrity Error: " + str(integrity_error)]}, status=HTTPStatus.BAD_REQUEST)

        except Exception as error:
            print(error)
            return JsonResponse({'success': False, 'errors': ["An unexpected error occurred. Please try again."]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    elif request.method == 'GET':
        status_choices = STATUS_CHOICES
        user = User.objects.get(pk=request.user.id)
        company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
        tickets = Ticket.objects.filter(segment__project__company=company)
        phases = Phase.objects.filter(company=company)
        segments = Segment.objects.filter(project__company=company)
        projects = Project.objects.filter(company=company)

        context = {
                    'status_choices': status_choices, 
                    'tickets': tickets, 
                    'phases': phases, 
                    'segments': segments, 
                    'projects': projects, 
                }
        return render(request=request, template_name='sprints/create_sprint.html', context=context)


@login_required
def update_sprint(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id)
    if request.method == 'POST':
        tickets, phases, segments, projects = [], [], [], []
        try:
            data = request.POST
            # required_fields = ['title', 'start_date', 'end_date', 'status', 'tickets', 'phases', 'segments', 'projects']
            required_fields = ['title', 'start_date', 'end_date']
            # Check for missing required fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'success': False, 'errors': f'Missing fields: {", ".join(missing_fields)}'}, status=HTTPStatus.BAD_REQUEST)

            if 'title' in data:
                title = data['title']
            if 'start_date' in data:
                start_date = data.get('start_date')
            if 'end_date' in data:
                end_date = data.get('end_date')
            if 'status' in data:
                status = data.get('status', OPEN)  # Default to OPEN if not provided
            if 'tickets' in data:
                tickets = data.getlist('tickets')  # Assuming tickets are received as a list of IDs
            if 'phases' in data:
                phases = data.getlist('phases')  # Assuming phases are received as a list of IDs
            if 'segments' in data:
                segments = data.getlist('segments')  # Assuming segments are received as a list of IDs
            if 'projects' in data:
                projects = data.getlist('projects')  # Assuming projects are received as a list of IDs

            # Basic validation
            errors = []
            if not title:
                errors.append("Title is required.")
            if not start_date:
                errors.append("Start date is required.")
            if not end_date:
                errors.append("End date is required.")
            if not status:
                errors.append("Status is required.")
            if not isinstance(tickets, list):
                errors.append("Tickets must be a list.")
            if not isinstance(phases, list):
                errors.append("Phases must be a list.")
            if not isinstance(segments, list):
                errors.append("Segments must be a list.")
            if not isinstance(projects, list):
                errors.append("Projects must be a list.")
            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

            with transaction.atomic():
                sprint.title = title
                sprint.start_date = start_date
                sprint.end_date = end_date
                sprint.status = status
                sprint.save(user=request.user)

                # Update SprintTicket model
                current_tickets = sprint.tickets.all()
                current_ticket_ids = set(current_tickets.values_list('id', flat=True))
                new_ticket_ids = set(map(int, tickets))

                tickets_to_add = new_ticket_ids - current_ticket_ids
                tickets_to_remove = current_ticket_ids - new_ticket_ids

                for ticket_id in tickets_to_add:
                    ticket = Ticket.objects.get(id=ticket_id)
                    SprintTicket.objects.create(sprint=sprint, ticket=ticket)

                for ticket_id in tickets_to_remove:
                    SprintTicket.objects.filter(sprint=sprint, ticket__id=ticket_id).delete()

                # Update SprintPhase model
                current_phases = sprint.phases.all()
                current_phase_ids = set(current_phases.values_list('id', flat=True))
                new_phase_ids = set(map(int, phases))

                phases_to_add = new_phase_ids - current_phase_ids
                phases_to_remove = current_phase_ids - new_phase_ids

                for phase_id in phases_to_add:
                    phase = Phase.objects.get(id=phase_id)
                    SprintPhase.objects.create(sprint=sprint, phase=phase)

                for phase_id in phases_to_remove:
                    SprintPhase.objects.filter(sprint=sprint, phase__id=phase_id).delete()

                # Update SprintSegment model
                current_segments = sprint.segments.all()
                current_segment_ids = set(current_segments.values_list('id', flat=True))
                new_segment_ids = set(map(int, segments))

                segments_to_add = new_segment_ids - current_segment_ids
                segments_to_remove = current_segment_ids - new_segment_ids

                for segment_id in segments_to_add:
                    segment = Segment.objects.get(id=segment_id)
                    SprintSegment.objects.create(sprint=sprint, segment=segment)

                for segment_id in segments_to_remove:
                    SprintSegment.objects.filter(sprint=sprint, segment__id=segment_id).delete()

                # Update SprintProject model
                current_projects = sprint.projects.all()
                current_project_ids = set(current_projects.values_list('id', flat=True))
                new_project_ids = set(map(int, projects))

                projects_to_add = new_project_ids - current_project_ids
                projects_to_remove = current_project_ids - new_project_ids

                for project_id in projects_to_add:
                    project = Project.objects.get(id=project_id)
                    SprintProject.objects.create(sprint=sprint, project=project)

                for project_id in projects_to_remove:
                    SprintProject.objects.filter(sprint=sprint, project__id=project_id).delete()


            # Fetch updated sprint again to ensure you have the latest data
            sprint = Sprint.objects.get(id=sprint_id)

            # Prepare context for rendering the update form with the updated sprint
            status_choices = STATUS_CHOICES
            user = User.objects.get(pk=request.user.id)
            company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
            tickets = Ticket.objects.filter(segment__project__company=company)
            phases = Phase.objects.filter(company=company)
            segments = Segment.objects.filter(project__company=company)
            projects = Project.objects.filter(company=company)

            context = {
                'sprint': sprint,
                'status_choices': status_choices,
                'tickets': tickets,
                'phases': phases,
                'segments': segments,
                'projects': projects,
            }
            return render(request, 'sprints/update_sprint.html', context=context)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': ["Invalid JSON data."]}, status=HTTPStatus.BAD_REQUEST)

        except IntegrityError as integrity_error:
            return JsonResponse({'success': False, 'errors': ["Integrity Error: " + str(integrity_error)]}, status=HTTPStatus.BAD_REQUEST)

        except Exception as error:
            print(error)
            return JsonResponse({'success': False, 'errors': ["An unexpected error occurred. Please try again."]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    elif request.method == 'GET':
        # Prepare context for rendering the update form with the updated sprint
        status_choices = STATUS_CHOICES
        user = User.objects.get(pk=request.user.id)
        company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
        tickets = Ticket.objects.filter(segment__project__company=company)
        phases = Phase.objects.filter(company=company)
        segments = Segment.objects.filter(project__company=company)
        projects = Project.objects.filter(company=company)

        context = {
            'sprint': sprint,
            'status_choices': status_choices,
            'tickets': tickets,
            'phases': phases,
            'segments': segments,
            'projects': projects,
        }
        return render(request, 'sprints/update_sprint.html', context=context)


@login_required
def get_all_sprints(request):
    user = request.user
    company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
    sprints = Sprint.objects.filter(company=company).order_by('-id')
    
    context = {
        'sprints': sprints
    }
    return render(request, 'sprints/sprint_list.html', context)
