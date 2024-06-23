from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from .models import Segment, SegmentAssignment, STATUS_CHOICES, OPEN
from projects.models import Project
from accounts.models import CustomerCompanyDetails, Company
from accounts.views import User
from http import HTTPStatus
import json


@login_required
def create_segment(request):
    if request.method == 'POST':
        assigned_to = []
        try:
            data = request.POST
            # required_fields = ['title', 'description', 'start_date', 'end_date', 'status', 'project_id', 'assigned_to']
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
                status = data.get('status', OPEN)  # Default to OPEN if not provided
            if 'project_id' in data:
                project_id = data['project_id']
            if 'assigned_to' in data:
                assigned_to = data.getlist('assigned_to')  # Assuming assigned_to are received as a list of IDs


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
            # if not project_id:
            #     errors.append("Project is required.")
            # if not isinstance(assigned_to, list):
            #     errors.append("Assigned to must be a list of user IDs.")
            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

            with transaction.atomic():
                # Getting company
                company = CustomerCompanyDetails.objects.filter(company_root_user=request.user).first().company
                project_objects = Project.objects.filter(id=project_id)
                
                segment = Segment()
                segment.title = title
                segment.description = description
                segment.start_date = start_date
                segment.end_date = end_date
                segment.status = status
                if project_objects.exists():
                    segment.project = project_objects.first()
                segment.save()

                segment.members.add(request.user) # this will add the current user itself as a member to the segment.

                # Add the current user to assigned_to list if not already included
                if str(request.user.id) not in assigned_to:
                    assigned_to.append(str(request.user.id))

                # Create related SegmentAssignment records
                for user_id in assigned_to:
                    user = User.objects.filter(id=user_id).first()
                    # Adding all invited users to members
                    segment.members.add(user)
                    if user:
                        SegmentAssignment.objects.create(segment=segment, assigned_by=request.user, assigned_to=user)

            return redirect('segments:segment_list')

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
        projects = Project.objects.filter(company=company)

        # Retrieve all unique users related to the company
        customer_company_details = CustomerCompanyDetails.objects.filter(company=company)
        company_root_user_ids = customer_company_details.values_list('company_root_user_id', flat=True)
        company_user_ids = customer_company_details.values_list('company_user_id', flat=True)
        all_user_ids = set(company_root_user_ids).union(set(company_user_ids))
        same_company_users = User.objects.filter(id__in=all_user_ids)
        
        context = {
                    'status_choices': status_choices, 
                    'projects': projects, 
                    'same_company_users': same_company_users
                }
        return render(request=request, template_name='segments/create_segment.html', context=context)



@login_required
def update_segment(request, segment_id):
    segment = get_object_or_404(Segment, id=segment_id)
    if request.method == 'POST':
        assigned_to_ids = []
        try:
            data = request.POST
            # required_fields = ['title', 'description', 'start_date', 'end_date', 'status', 'project_id', 'assigned_to']
            required_fields = ['title']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'success': False, 'errors': f'Missing fields: {", ".join(missing_fields)}'}, status=HTTPStatus.BAD_REQUEST)
            
            title = data['title']
            description = data.get('description', '')
            start_date = data.get('start_date', None)
            end_date = data.get('end_date', None)
            status = data.get('status', OPEN)  # Default to OPEN if not provided
            project_id = data.get('project_id', None)

            errors = []
            if not title:
                errors.append("Title is required.")
            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

            # Convert phases and assigned_to to lists if they are not already
            assigned_to_ids = data.getlist('assigned_to')  # Assuming assigned_to are received as a list of IDs

            with transaction.atomic():
                segment.title = title
                segment.description = description
                segment.start_date = start_date
                segment.end_date = end_date
                segment.status = status
                if project_id:
                    project_objects = Project.objects.filter(id=project_id)
                    if project_objects.exists():
                        segment.project = project_objects.first()
                segment.save()

                # Ensure current requested user is added as a member if not already.
                if request.user not in segment.members.all():
                    segment.members.add(request.user)

                # Update members via ManyToManyField
                current_members = set(segment.members.all())
                new_members = set(User.objects.filter(id__in=assigned_to_ids))

                # Add new members
                members_to_add = new_members - current_members
                for member in members_to_add:
                    segment.members.add(member)

                # Remove old members except the current requested user.
                members_to_remove = current_members - new_members
                for member in members_to_remove:
                    # Avoid removing the current user from members
                    if member != request.user:
                        segment.members.remove(member)

                # Update members via SegmentAssignment model
                current_assignments = SegmentAssignment.objects.filter(segment=segment)
                current_assignment_user_ids = set(current_assignments.values_list('assigned_to', flat=True))
                new_assignment_user_ids = set(map(int, assigned_to_ids))

                assignments_to_add = new_assignment_user_ids - current_assignment_user_ids
                assignments_to_remove = current_assignment_user_ids - new_assignment_user_ids

                for user_id in assignments_to_add:
                    user = User.objects.get(id=user_id)
                    SegmentAssignment.objects.create(segment=segment, assigned_by=request.user, assigned_to=user)

                for user_id in assignments_to_remove:
                    SegmentAssignment.objects.filter(segment=segment, assigned_to=user_id).delete()

            # Fetch updated segment again to ensure you have the latest data
            segment = Segment.objects.get(id=segment_id)

            # Prepare context for rendering the update form with the updated segment
            status_choices = STATUS_CHOICES
            user = User.objects.get(pk=request.user.id)
            company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
            projects = Project.objects.filter(company=company)

            customer_company_details = CustomerCompanyDetails.objects.filter(company=company)
            company_root_user_ids = customer_company_details.values_list('company_root_user_id', flat=True)
            company_user_ids = customer_company_details.values_list('company_user_id', flat=True)
            all_user_ids = set(company_root_user_ids).union(set(company_user_ids))
            same_company_users = User.objects.filter(id__in=all_user_ids)

            context = {
                'segment': segment,
                'status_choices': status_choices,
                'projects': projects,
                'same_company_users': same_company_users,
            }
            return render(request, 'segments/update_segment.html', context=context)

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
        projects = Project.objects.filter(company=company)

        customer_company_details = CustomerCompanyDetails.objects.filter(company=company)
        company_root_user_ids = customer_company_details.values_list('company_root_user_id', flat=True)
        company_user_ids = customer_company_details.values_list('company_user_id', flat=True)
        all_user_ids = set(company_root_user_ids).union(set(company_user_ids))
        same_company_users = User.objects.filter(id__in=all_user_ids)
        
        context = {
            'segment': segment,
            'status_choices': status_choices, 
            'projects': projects, 
            'same_company_users': same_company_users
        }
        return render(request=request, template_name='segments/update_segment.html', context=context)



@login_required
def get_all_segments(request):
    user = request.user
    company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
    segments = Segment.objects.filter(project__company=company).order_by('-id')
    
    context = {
        'segments': segments
    }
    return render(request, 'segments/segment_list.html', context)
