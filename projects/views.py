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
            # required_fields = ['title', 'description', 'start_date', 'end_date', 'status', 'phases', 'assigned_to']
            required_fields = ['title']
            # Check for missing required fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'success': False, 'errors': f'Missing fields: {", ".join(missing_fields)}'}, status=HTTPStatus.BAD_REQUEST)

            title = data['title']
            description = data.get('description', '')  # Description is optional
            start_date = data.get('start_date', None)
            end_date = data.get('end_date', None)
            status = data.get('status', '')  # Status is optional
            phases = data['phases']
            assigned_to = data['assigned_to']

            # Basic validation
            errors = []
            if not title:
                errors.append("Title is required.")
            # if not start_date:
            #     errors.append("Start date is required.")
            # if not end_date:
            #     errors.append("End date is required.")
            # if not status:
            #     errors.append("Status is required.")
            # if not isinstance(phases, list):
            #     errors.append("Phases must be a list.")
            # if not isinstance(assigned_to, list):
            #     errors.append("Assigned to must be a list of user IDs.")
            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

            with transaction.atomic():
                # Getting company
                company = CustomerCompanyDetails.objects.filter(company_root_user=request.user).first().company

                project = Project.objects.create(
                    title=title,
                    description=description,
                    start_date=start_date,
                    end_date=end_date,
                    status=status,
                    company=company
                )
                

                project.members.add(request.user) # this will add the current user itself as a member to the project.

                # Create related ProjectPhase records
                for phase_id in phases:
                    each_phase = Phase.objects.filter(id=phase_id).first()
                    if each_phase:
                        ProjectPhase.objects.create(project=project, phase=each_phase)

                ProjectAssignment.objects.create(project=project, assigned_by=request.user)

                # Create related ProjectAssignment records
                for user_id in assigned_to:
                    user = User.objects.filter(id=user_id).first()
                    # Adding all invited users to members
                    project.members.add(user)
                    if user:
                        ProjectAssignment.objects.create(project=project, assigned_to=user)

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

        # Retrieve all unique users related to the company
        customer_company_details = CustomerCompanyDetails.objects.filter(company=company)
        company_root_user_ids = customer_company_details.values_list('company_root_user_id', flat=True)
        company_user_ids = customer_company_details.values_list('company_user_id', flat=True)
        all_user_ids = set(company_root_user_ids).union(set(company_user_ids))
        same_company_users = User.objects.filter(id__in=all_user_ids)
        
        context = {
                    'status_choices': status_choices, 
                    'phases': phases, 
                    'same_company_users': same_company_users
                }
        return render(request=request, template_name='projects/create_project.html', context=context)