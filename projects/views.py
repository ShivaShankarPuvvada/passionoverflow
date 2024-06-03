from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from .models import Project, ProjectPhase, ProjectAssignment, STATUS_CHOICES
from accounts.models import CustomerCompanyDetails, Company
from phases.models import Phase
from accounts.views import User
from http import HTTPStatus
import json


@login_required
def create_project(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            required_fields = ['title', 'description', 'start_date', 'end_date', 'status', 'phases', 'assigned_to']
            
            # Check for missing required fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'success': False, 'errors': f'Missing fields: {", ".join(missing_fields)}'}, status=HTTPStatus.BAD_REQUEST)

            title = data['title']
            description = data['description']
            start_date = data['start_date']
            end_date = data['end_date']
            status = data['status']
            phases_data = data['phases']
            assigned_to = data['assigned_to']

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
            if not isinstance(phases_data, list):
                errors.append("Phases must be a list.")
            if not isinstance(assigned_to, list):
                errors.append("Assigned to must be a list of user IDs.")
            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

            with transaction.atomic():
                project = Project.objects.create(
                    title=title,
                    description=description,
                    start_date=start_date,
                    end_date=end_date,
                    status=status
                )

                # Create related ProjectPhase records
                for phase_data in phases_data:
                    ProjectPhase.objects.create(project=project, **phase_data)

                # Create related ProjectAssignment records
                for user_id in assigned_to:
                    ProjectAssignment.objects.create(project=project, assigned_to_id=user_id)

            return JsonResponse({'success': True, 'redirect_url': reverse('projects:project_list')})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': ["Invalid JSON data."]}, status=HTTPStatus.BAD_REQUEST)

        except IntegrityError as integrity_error:
            return JsonResponse({'success': False, 'errors': ["Integrity Error: " + str(integrity_error)]}, status=HTTPStatus.BAD_REQUEST)

        except Exception as error:
            return JsonResponse({'success': False, 'errors': ["An unexpected error occurred. Please try again."]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    elif request.method == 'GET':
        status_choices = STATUS_CHOICES
        user = User.objects.get(pk=request.user.id)
        company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
        phases = Phase.objects.filter(company=company)
        return render(request, 'projects/create_project.html', {'status_choices': status_choices, 'phases': phases})
