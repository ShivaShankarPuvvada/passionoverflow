from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from .models import Stage, STATUS_CHOICES, OPEN
from accounts.models import CustomerCompanyDetails, Company
from accounts.views import User
from http import HTTPStatus
import json


# Create your views here.

@login_required
def create_stage(request):
    if request.method == 'POST':
        try:
            data = request.POST
            # required_fields = ['title', 'status']
            required_fields = ['title']
            # Check for missing required fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'success': False, 'errors': f'Missing fields: {", ".join(missing_fields)}'}, status=HTTPStatus.BAD_REQUEST)

            if 'title' in data:
                title = data.get('title', '').strip()
            if 'status' in data:
                status = data.get('status', OPEN)  # Default to OPEN if not provided

            # Basic validation
            errors = []
            if not title:
                errors.append("Title is required.")
            # if not status:
            #     errors.append("Status is required.")
            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

            with transaction.atomic():
                # Getting company
                contributor = CustomerCompanyDetails.objects.filter(company_root_user=request.user)
                collaborator = CustomerCompanyDetails.objects.filter(company_user=request.user)
                if contributor.exists():
                    company = contributor.first().company
                elif collaborator.exists():
                    company = collaborator.first().company
                stage = Stage.objects.create(
                    title=title,
                    status=status,
                    company=company,
                )

            return redirect('stages:stage_list')

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': ["Invalid JSON data."]}, status=HTTPStatus.BAD_REQUEST)

        except IntegrityError as integrity_error:
            return JsonResponse({'success': False, 'errors': ["Integrity Error: " + str(integrity_error)]}, status=HTTPStatus.BAD_REQUEST)

        except Exception as error:
            print(error)
            return JsonResponse({'success': False, 'errors': ["An unexpected error occurred. Please try again."]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    elif request.method == 'GET':
        status_choices = STATUS_CHOICES
        context = {
                    'status_choices': status_choices, 
                }
        return render(request=request, template_name='stages/create_stage.html', context=context)

@login_required
def create_stage_from_kanban(request):
    if request.method == 'POST':
        try:
            data = request.POST
            required_fields = ['title']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'success': False, 'errors': f'Missing fields: {", ".join(missing_fields)}'}, status=HTTPStatus.BAD_REQUEST)

            title = data.get('title', '').strip()
            status = data.get('status', OPEN)

            errors = []
            if not title:
                errors.append("Title is required.")
            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

            with transaction.atomic():
                contributor = CustomerCompanyDetails.objects.filter(company_root_user=request.user)
                collaborator = CustomerCompanyDetails.objects.filter(company_user=request.user)
                if contributor.exists():
                    company = contributor.first().company
                elif collaborator.exists():
                    company = collaborator.first().company
                stage = Stage.objects.create(
                    title=title,
                    status=status,
                    company=company,
                )

            # Return the created stage as JSON
            return JsonResponse({'success': True, 'stage': {'id': stage.id, 'title': stage.title}})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': ["Invalid JSON data."]}, status=HTTPStatus.BAD_REQUEST)

        except IntegrityError as integrity_error:
            return JsonResponse({'success': False, 'errors': ["Integrity Error: " + str(integrity_error)]}, status=HTTPStatus.BAD_REQUEST)


@login_required
def update_stage(request, stage_id):
    stage = get_object_or_404(Stage, id=stage_id)
    if request.method == 'POST':
        try:
            data = request.POST
            required_fields = ['title']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'success': False, 'errors': f'Missing fields: {", ".join(missing_fields)}'}, status=HTTPStatus.BAD_REQUEST)
            
            title = data['title']
            status = data.get('status', OPEN)  # Default to OPEN if not provided

            errors = []
            if not title:
                errors.append("Title is required.")
            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

            with transaction.atomic():
                user = User.objects.get(pk=request.user.id)

                stage.title = title
                stage.status = status
                stage.save(user=request.user)
                

            # Prepare context for rendering the update form with the updated stage
            status_choices = STATUS_CHOICES
            context = {
                'stage': stage,
                'status_choices': status_choices,
            }
            return render(request, 'stages/update_stage.html', context=context)

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
        context = {
            'stage': stage,
            'status_choices': status_choices, 
        }
        return render(request=request, template_name='stages/update_stage.html', context=context)


@login_required
def get_all_stages(request):
    contributor = CustomerCompanyDetails.objects.filter(company_root_user=request.user)
    collaborator = CustomerCompanyDetails.objects.filter(company_user=request.user)
    if contributor.exists():
        company = contributor.first().company
    elif collaborator.exists():
        company = collaborator.first().company
    stages = Stage.objects.filter(company=company).order_by('-id')
    
    context = {
        'stages': stages
    }
    return render(request, 'stages/stage_list.html', context)


@csrf_exempt  # Use only if you're not using CSRF tokens for AJAX requests
@require_POST
def update_stage_from_kanban(request):
    # Extract the stage ID and title from the request
    stage_id = request.GET.get('id')
    new_title = request.POST.get('title')
    
    # Ensure that we have the stage ID and title
    if not stage_id:
        return JsonResponse({'success': False, 'error': 'Stage ID not provided'})
    if not new_title:
        return JsonResponse({'success': False, 'error': 'Title not provided'})
    
    # Retrieve the stage object from the database
    try:
        stage = Stage.objects.get(pk=stage_id)
    except Stage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Stage not found'})
    
    # Check if the title has changed
    if stage.title == new_title:
        return JsonResponse({'success': True, 'message': 'No changes made to the title'})
    
    # Update the stage title and save
    stage.title = new_title
    stage.save()
    
    return JsonResponse({'success': True, 'id': stage.id, 'newTitle': stage.title})
