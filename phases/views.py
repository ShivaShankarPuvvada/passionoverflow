from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from .models import Phase, STATUS_CHOICES, OPEN
from accounts.models import CustomerCompanyDetails, Company
from phases.models import Phase
from accounts.views import User
from http import HTTPStatus
import json


# Create your views here.

@login_required
def create_phase(request):
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
                company = CustomerCompanyDetails.objects.filter(company_root_user=request.user).first().company

                phase = Phase.objects.create(
                    title=title,
                    status=status,
                    company=company,
                )

            return redirect('phases:phase_list')

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
        return render(request=request, template_name='phases/create_phase.html', context=context)


@login_required
def update_phase(request, phase_id):
    phase = get_object_or_404(Phase, id=phase_id)
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
                is_contributor = CustomerCompanyDetails.objects.filter(company_root_user=user)
                if is_contributor.exists():
                    phase.title = title
                    phase.status = status
                    phase.save()
                else:
                    return JsonResponse({'success': False, 'errors': errors.append('Only contributor can have access to Phases.')}, status=HTTPStatus.BAD_REQUEST)


            # Prepare context for rendering the update form with the updated phase
            status_choices = STATUS_CHOICES
            context = {
                'phase': phase,
                'status_choices': status_choices,
            }
            return render(request, 'phases/update_phase.html', context=context)

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
        is_contributor = CustomerCompanyDetails.objects.filter(company_root_user=user)
        if is_contributor.exists():
            context = {
                'phase': phase,
                'status_choices': status_choices, 
            }
            return render(request=request, template_name='phases/update_phase.html', context=context)


@login_required
def get_all_phases(request):
    user = request.user
    company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
    phases = Phase.objects.filter(company=company).order_by('-id')
    
    context = {
        'phases': phases
    }
    return render(request, 'phases/phase_list.html', context)
