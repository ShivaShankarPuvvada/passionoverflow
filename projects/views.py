from django.shortcuts import render, redirect, get_object_or_404
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
        phases, assigned_to = [], []
        try:
            data = request.POST
            # required_fields = ['title', 'description', 'start_date', 'end_date', 'status', 'phases', 'assigned_to']
            required_fields = ['title']
            # Check for missing required fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'success': False, 'errors': f'Missing fields: {", ".join(missing_fields)}'}, status=HTTPStatus.BAD_REQUEST)

            if 'title' in data:
                title = data['title']
            if 'description' in data:
                description = data.get('description', '')  # Description is optional
            if 'start_date' in data:
                start_date = data.get('start_date', None)
            if 'end_date' in data:
                end_date = data.get('end_date', None)
            if 'status' in data:
                status = data.get('status', '')  # Status is optional
            if 'phases' in data:
                phases = data['phases']
            if 'assigned_to' in data:
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

                # Create related ProjectAssignment records
                for user_id in assigned_to:
                    user = User.objects.filter(id=user_id).first()
                    # Adding all invited users to members
                    project.members.add(user)
                    if user:
                        ProjectAssignment.objects.create(project=project, assigned_by=request.user, assigned_to=user)

            return redirect('projects:project_list')

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


@login_required
def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        phase_ids, assigned_to_ids = [], []
        try:
            data = request.POST
            required_fields = ['title']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'success': False, 'errors': f'Missing fields: {", ".join(missing_fields)}'}, status=HTTPStatus.BAD_REQUEST)
            
            title = data['title']
            description = data.get('description', '')
            start_date = data.get('start_date', None)
            end_date = data.get('end_date', None)
            status = data.get('status', '')

            errors = []
            if not title:
                errors.append("Title is required.")
            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

            # Convert phases and assigned_to to lists if they are not already
            phase_ids = data.getlist('phases')  # Assuming phases are received as a list of IDs
            assigned_to_ids = data.getlist('assigned_to')  # Assuming assigned_to are received as a list of IDs

            with transaction.atomic():
                project.title = title
                project.description = description
                project.start_date = start_date
                project.end_date = end_date
                project.status = status
                project.save()

                # Ensure current requested user is added as a member if not already.
                if request.user not in project.members.all():
                    project.members.add(request.user)

                # Update members via ManyToManyField
                current_members = set(project.members.all())
                new_members = set(User.objects.filter(id__in=assigned_to_ids))

                # Add new members
                members_to_add = new_members - current_members
                for member in members_to_add:
                    project.members.add(member)

                # Remove old members except the current requested user.
                members_to_remove = current_members - new_members
                for member in members_to_remove:
                    # Avoid removing the current user from members
                    if member != request.user:
                        project.members.remove(member)

                # Update members via ProjectAssignment model
                current_assignments = ProjectAssignment.objects.filter(project=project)
                current_assignment_user_ids = set(current_assignments.values_list('assigned_to', flat=True))
                new_assignment_user_ids = set(map(int, assigned_to_ids))

                assignments_to_add = new_assignment_user_ids - current_assignment_user_ids
                assignments_to_remove = current_assignment_user_ids - new_assignment_user_ids

                for user_id in assignments_to_add:
                    user = User.objects.get(id=user_id)
                    ProjectAssignment.objects.create(project=project, assigned_by=request.user, assigned_to=user)

                for user_id in assignments_to_remove:
                    ProjectAssignment.objects.filter(project=project, assigned_to=user_id).delete()

                # Update ProjectPhases
                current_phases = project.phases.all()
                current_phase_ids = set(current_phases.values_list('id', flat=True))
                new_phase_ids = set(map(int, phase_ids))

                phases_to_add = new_phase_ids - current_phase_ids
                phases_to_remove = current_phase_ids - new_phase_ids

                for phase_id in phases_to_add:
                    phase = Phase.objects.get(id=phase_id)
                    ProjectPhase.objects.create(project=project, phase=phase)

                for phase_id in phases_to_remove:
                    ProjectPhase.objects.filter(project=project, phase_id=phase_id).delete()

            # Fetch updated project again to ensure you have the latest data
            project = Project.objects.get(id=project_id)

            # Prepare context for rendering the update form with the updated project
            status_choices = STATUS_CHOICES
            user = User.objects.get(pk=request.user.id)
            company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
            phases = Phase.objects.filter(company=company)

            customer_company_details = CustomerCompanyDetails.objects.filter(company=company)
            company_root_user_ids = customer_company_details.values_list('company_root_user_id', flat=True)
            company_user_ids = customer_company_details.values_list('company_user_id', flat=True)
            all_user_ids = set(company_root_user_ids).union(set(company_user_ids))
            same_company_users = User.objects.filter(id__in=all_user_ids)

            context = {
                'project': project,
                'status_choices': status_choices,
                'phases': phases,
                'same_company_users': same_company_users,
            }
            return render(request, 'projects/update_project.html', context=context)

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
        phases = Phase.objects.filter(company=company)

        customer_company_details = CustomerCompanyDetails.objects.filter(company=company)
        company_root_user_ids = customer_company_details.values_list('company_root_user_id', flat=True)
        company_user_ids = customer_company_details.values_list('company_user_id', flat=True)
        all_user_ids = set(company_root_user_ids).union(set(company_user_ids))
        same_company_users = User.objects.filter(id__in=all_user_ids)
        
        context = {
            'project': project,
            'status_choices': status_choices, 
            'phases': phases, 
            'same_company_users': same_company_users
        }
        return render(request=request, template_name='projects/update_project.html', context=context)


@login_required
def get_all_projects(request):
    user = request.user
    company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
    projects = Project.objects.filter(company=company).order_by('-start_date')
    
    context = {
        'projects': projects
    }
    return render(request, 'projects/project_list.html', context)


def get_all_projects(request):
    user = request.user
    company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
    projects = Project.objects.filter(company=company).order_by('-start_date')
    
    context = {
        'projects': projects
    }
    return render(request, 'projects/project_list.html', context)

