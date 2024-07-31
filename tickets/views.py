from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from .models import Ticket, TicketStage, TicketAssignment
from accounts.models import CustomerCompanyDetails, Company
from stages.models import Stage
from projects.models import Project
from segments.models import Segment
from tags.models import Tag
from accounts.views import User
from http import HTTPStatus
import json

from stages.models import Stage, STATUS_CHOICES as STAGE_STATUS_CHOICES, OPEN as STAGE_OPEN



"""
Ticket will be visible to only to people who are in the segment.
Ticket can be moved to another segment.
"""
@login_required
def create_ticket(request):
    if request.method == 'POST':
        super_tickets, sub_tickets, tags, assigned_to = [], [], [], []
        try:
            data = request.POST
            # required_fields = ['super_tickets', 'sub_tickets', 'title', 'description', 'start_date', 'end_date', 
            # 'estimated_end_date', 'due_date', 'status', 'stages', 'priority_type', 'priority', 'priority_scale', 
            # 'ticket_type', 'segment_id', 'assigned_to', 'tags']
            required_fields = ['title']
            # Check for missing required fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'success': False, 'errors': f'Missing fields: {", ".join(missing_fields)}'}, status=HTTPStatus.BAD_REQUEST)

            if 'super_tickets' in data:
                super_tickets = data.getlist('super_tickets')
            if 'sub_tickets' in data:
                sub_tickets = data.getlist('sub_tickets')
            if 'title' in data:
                title = data['title']
            if 'description' in data:
                description = data.get('description', '')  # Description is optional
            if 'start_date' in data:
                start_date = data.get('start_date', None)
            if 'end_date' in data:
                end_date = data.get('end_date', None)
            if 'estimated_end_date' in data:
                estimated_end_date = data.get('estimated_end_date', None)
            if 'due_date' in data:
                due_date = data.get('due_date', None)
            if 'status' in data:
                status = data.get('status', Ticket.Status.ACTIVE)  # Default to OPEN if not provided
            if 'stages' in data:
                stages = data.get('stages')  # Assuming stages is a single id.
            # if 'priority_type' in data:
            #     priority_type = data.get('priority_type', Ticket.PriorityType.TEXTOPTION)
            # if 'priority' in data:
            #     priority = data.get('priority', Ticket.Priority.MEDIUM)
            if 'priority_scale' in data:
                priority_scale = data.get('priority_scale', Ticket.PriorityScale.FIVE)
            if 'ticket_type' in data:
                ticket_type = data.get('ticket_type', Ticket.TicketType.FEATURE)
            if 'segment_id' in data:
                segment_id = data.get('segment_id')
            if 'tags' in data:
                tags = data.getlist('tags')
            if 'assigned_to' in data:
                assigned_to = data.getlist('assigned_to')  # Assuming assigned_to are received as a list of IDs

            # Check for common tickets in super and sub tickets
            if super_tickets and sub_tickets:
                common_tickets = list(set(super_tickets) & set(sub_tickets))
                if common_tickets:
                    error = f'Ticket(s) {", ".join(map(str, common_tickets))} cannot be both super and sub tickets.'
                    errors.append(error)

            # Basic validation
            errors = []
            if not title:
                errors.append("Title is required.")

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

                ticket = Ticket()
                ticket.title=title
                ticket.description=description
                ticket.start_date=start_date
                ticket.end_date=end_date
                ticket.estimated_end_date=estimated_end_date
                ticket.due_date=due_date
                ticket.status=status
                # ticket.priority_type=priority_type,
                # ticket.priority=priority,
                ticket.priority_scale=priority_scale
                ticket.ticket_type=ticket_type
                if segment_id:
                    segment_objects = Segment.objects.filter(id=segment_id)
                    if segment_objects.exists():
                        ticket.segment = segment_objects.first()
                
                ticket.save(user=request.user)


                ticket.members.add(request.user) # this will add the current user itself as a member to the ticket.

                # Add super tickets
                for super_ticket_id in super_tickets:
                    super_ticket = Ticket.objects.get(pk=super_ticket_id)
                    ticket.super_tickets.add(super_ticket)

                # Add sub tickets
                for sub_ticket_id in sub_tickets:
                    sub_ticket = Ticket.objects.get(pk=sub_ticket_id)
                    ticket.sub_tickets.add(sub_ticket)

                # Add tags
                for tag_id in tags:
                    tag = Tag.objects.get(pk=tag_id)
                    ticket.tags.add(tag)


                # adding the assigned to persons as segment members if they are new to the segment. 
                for user_id in assigned_to:
                    user = User.objects.get(pk=user_id)  # Fetch the User object based on user_id
                    if user not in ticket.segment.members.all():
                        ticket.segment.members.add(user)


                # Create related TicketStage records, A ticket can be at a single stage at one time.
                stage = Stage.objects.filter(id=stages).first()
                if stage:
                    TicketStage.objects.create(ticket=ticket, stage=stage, active=True)

                # Add the current user to assigned_to list if not already included
                if str(request.user.id) not in assigned_to:
                    assigned_to.append(str(request.user.id))

                # write a function here, it will add the users to the segment if they are not already in the segment.
                # An ajax function should tell by clicking create ticket if users are not in the segment and we should add them.
                # If collaborator is trying to create a ticket then it should mail it to the contributors. currently sending segment only users to the ticket.

                # Create related TicketAssignment records
                for user_id in assigned_to:
                    user = User.objects.filter(id=user_id).first()
                    # Adding all invited users to members
                    ticket.members.add(user)
                    if user:
                        TicketAssignment.objects.create(ticket=ticket, assigned_by=request.user, assigned_to=user)

            return redirect('tickets:ticket_list')

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': ["Invalid JSON data."]}, status=HTTPStatus.BAD_REQUEST)

        except IntegrityError as integrity_error:
            return JsonResponse({'success': False, 'errors': ["Integrity Error: " + str(integrity_error)]}, status=HTTPStatus.BAD_REQUEST)

        except Exception as error:
            print(error)
            import os,sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return JsonResponse({'success': False, 'errors': ["An unexpected error occurred. Please try again."]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    elif request.method == 'GET':
        # sending all choices to template
        status_choices = Ticket.Status.choices
        priority_scale = Ticket.PriorityScale.choices
        ticket_type = Ticket.TicketType.choices

        # checking type of user and getting company
        user = User.objects.get(pk=request.user.id)
        contributor = CustomerCompanyDetails.objects.filter(company_root_user=user)
        collaborator = CustomerCompanyDetails.objects.filter(company_user=user)
        if contributor.exists():
            company = contributor.first().company
        elif collaborator.exists():
            company = collaborator.first().company
        
        # getting all the segments he is involved in. 
        # He should be able to create ticket in all segments he is involved in.
        segments = Segment.objects.filter(project__company=company, members=user)

        # Getting all stages related to the company
        stages = Stage.objects.filter(company=company)
        
        # Getting all tags related to the company
        tags = Tag.objects.filter(company=company)

        # Getting all tickets related to the company
        tickets = Ticket.objects.filter(segment__project__company=company)

        # Retrieve all unique users related to the company
        customer_company_details = CustomerCompanyDetails.objects.filter(company=company)
        company_root_user_ids = customer_company_details.values_list('company_root_user_id', flat=True)
        company_user_ids = customer_company_details.values_list('company_user_id', flat=True)
        all_user_ids = set(company_root_user_ids).union(set(company_user_ids))
        same_company_users = User.objects.filter(id__in=all_user_ids)

        # Retrieve all unique users related to the all segments. 
        # If the required user is not in the selected segments, contributor need to assign him to segment.
        # currently sending all users related to company only.
        # if the selected users were not in the selected segment, it will directly add the new users to segment members.
        # we will send mail to contributor that you requested them to add to the selected segment.
        # If current user is a contributor, we will directly add them to the segment.
        # currently for all, we are directly adding them to the segment. Only collaborators can't directly add others to the project.
        context = {
                    'tags': tags,
                    'stages': stages, 
                    'tickets': tickets,
                    'segments': segments,
                    'ticket_type': ticket_type,
                    'status_choices': status_choices,
                    'priority_scale': priority_scale,
                    'same_company_users': same_company_users
                }
        return render(request=request, template_name='tickets/create_ticket.html', context=context)


@login_required
def update_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        stage_ids, assigned_to_ids = [], []
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
            estimated_end_date = data.get('estimated_end_date', None)
            due_date = data.get('due_date', None)
            status = data.get('status', Ticket.Status.ACTIVE)
            priority_scale = data.get('priority_scale', Ticket.PriorityScale.FIVE)
            ticket_type = data.get('ticket_type', Ticket.TicketType.FEATURE)
            segment_id = data.get('segment_id')
            stages = data.get('stages')  # Assuming stages is a single id.
            super_tickets = data.getlist('super_tickets', [])
            sub_tickets = data.getlist('sub_tickets', [])
            tags = data.getlist('tags', [])
            assigned_to = data.getlist('assigned_to', [])

            errors = []
            if not title:
                errors.append("Title is required.")

            # Check for common tickets in super and sub tickets
            if super_tickets and sub_tickets:
                common_tickets = list(set(super_tickets) & set(sub_tickets))
                if common_tickets:
                    error = f'Ticket(s) {", ".join(map(str, common_tickets))} cannot be both super and sub tickets.'
                    errors.append(error)

            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=HTTPStatus.BAD_REQUEST)

            
            with transaction.atomic():
                ticket.title = title
                ticket.description = description
                ticket.start_date = start_date
                ticket.end_date = end_date
                ticket.estimated_end_date = estimated_end_date
                ticket.due_date = due_date
                ticket.status = status
                ticket.priority_scale = priority_scale
                ticket.ticket_type = ticket_type
                if segment_id:
                    segment_objects = Segment.objects.filter(id=segment_id)
                    if segment_objects.exists():
                        ticket.segment = segment_objects.first()
                
                ticket.save(user=request.user)

                # Ensure current requested user is added as a member if not already.
                if request.user not in ticket.members.all():
                    ticket.members.add(request.user)

                # Update members via ManyToManyField
                current_members = set(ticket.members.all())
                new_members = set(User.objects.filter(id__in=assigned_to_ids))

                # Add new members
                members_to_add = new_members - current_members
                for member in members_to_add:
                    ticket.members.add(member)

                # Remove old members except the current requested user.
                members_to_remove = current_members - new_members
                for member in members_to_remove:
                    # Avoid removing the current user from members
                    if member != request.user:
                        ticket.members.remove(member)

                # Update members via TicketAssignment model
                current_assignments = TicketAssignment.objects.filter(ticket=ticket)
                current_assignment_user_ids = set(current_assignments.values_list('assigned_to', flat=True))
                new_assignment_user_ids = set(map(int, assigned_to_ids))

                assignments_to_add = new_assignment_user_ids - current_assignment_user_ids
                assignments_to_remove = current_assignment_user_ids - new_assignment_user_ids

                for user_id in assignments_to_add:
                    user = User.objects.get(id=user_id)
                    TicketAssignment.objects.create(ticket=ticket, assigned_by=request.user, assigned_to=user)

                for user_id in assignments_to_remove:
                    user = User.objects.get(id=user_id)
                    TicketAssignment.objects.filter(ticket=ticket, assigned_to=user).delete()

                # adding the assigned to persons as segment members if they are new to the segment. 
                for user_id in new_assignment_user_ids:
                    user = User.objects.get(pk=user_id)  # Fetch the User object based on user_id
                    if user not in ticket.segment.members.all():
                        ticket.segment.members.add(user)

                # if stages is a multiselect, use the below code with stage_ids = data.getlist('stages')
                # # Update TicketStages
                # current_stages = ticket.stages.all()
                # current_stage_ids = set(current_stages.values_list('id', flat=True))
                # new_stage_ids = set(map(int, stage_ids))

                # stages_to_add = new_stage_ids - current_stage_ids
                # stages_to_remove = current_stage_ids - new_stage_ids

                # for stage_id in stages_to_add:
                #     stage = Stage.objects.get(id=stage_id)
                #     TicketStage.objects.create(ticket=ticket, stage=stage)

                # for stage_id in stages_to_remove:
                #     stage = Stage.objects.get(id=stage_id)
                #     TicketStage.objects.filter(ticket=ticket, stage=stage).delete()
                # if stages is a multiselect, use the above code with stage_ids = data.getlist('stages')

                # Track super tickets changes
                current_super_tickets = set(ticket.super_tickets.all())
                new_super_tickets = set(Ticket.objects.filter(id__in=super_tickets))

                super_tickets_added = new_super_tickets - current_super_tickets
                super_tickets_removed = current_super_tickets - new_super_tickets

                for super_ticket in super_tickets_added:
                    ticket.super_tickets.add(super_ticket)

                for super_ticket in super_tickets_removed:
                    ticket.super_tickets.remove(super_ticket)

                print(f'Super tickets added: {len(super_tickets_added)}')
                print(f'Super tickets removed: {len(super_tickets_removed)}')

                # Track sub tickets changes
                current_sub_tickets = set(ticket.sub_tickets.all())
                new_sub_tickets = set(Ticket.objects.filter(id__in=sub_tickets))

                sub_tickets_added = new_sub_tickets - current_sub_tickets
                sub_tickets_removed = current_sub_tickets - new_sub_tickets

                for sub_ticket in sub_tickets_added:
                    ticket.sub_tickets.add(sub_ticket)

                for sub_ticket in sub_tickets_removed:
                    ticket.sub_tickets.remove(sub_ticket)

                print(f'Sub tickets added: {len(sub_tickets_added)}')
                print(f'Sub tickets removed: {len(sub_tickets_removed)}')

                # Update tags
                ticket.tags.clear()
                for tag_id in tags:
                    tag = Tag.objects.get(pk=tag_id)
                    ticket.tags.add(tag)

                # Update TicketStage records
                TicketStage.objects.filter(ticket=ticket, active=True).update(active=False)
                stage = Stage.objects.filter(id=stages).first()
                if stage:
                    TicketStage.objects.create(ticket=ticket, stage=stage, active=True)

            return redirect('tickets:ticket_list')

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': ["Invalid JSON data."]}, status=HTTPStatus.BAD_REQUEST)

        except IntegrityError as integrity_error:
            return JsonResponse({'success': False, 'errors': ["Integrity Error: " + str(integrity_error)]}, status=HTTPStatus.BAD_REQUEST)

        except Exception as error:
            print(error)
            return JsonResponse({'success': False, 'errors': ["An unexpected error occurred. Please try again."]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    elif request.method == 'GET':
        status_choices = Ticket.Status.choices
        priority_scale = Ticket.PriorityScale.choices
        ticket_type = Ticket.TicketType.choices

        user = User.objects.get(pk=request.user.id)
        contributor = CustomerCompanyDetails.objects.filter(company_root_user=user)
        collaborator = CustomerCompanyDetails.objects.filter(company_user=user)
        if contributor.exists():
            company = contributor.first().company
        elif collaborator.exists():
            company = collaborator.first().company
        
        segments = Segment.objects.filter(project__company=company, members=user)
        stages = Stage.objects.filter(company=company)
        tags = Tag.objects.filter(company=company)
        tickets = Ticket.objects.filter(segment__project__company=company)

        # Retrieve all unique users related to the company
        customer_company_details = CustomerCompanyDetails.objects.filter(company=company)
        company_root_user_ids = customer_company_details.values_list('company_root_user_id', flat=True)
        company_user_ids = customer_company_details.values_list('company_user_id', flat=True)
        all_user_ids = set(company_root_user_ids).union(set(company_user_ids))
        same_company_users = User.objects.filter(id__in=all_user_ids)

        context = {
            'ticket': ticket,
            'same_company_users': same_company_users,
            'tags': tags,
            'stages': stages,
            'tickets': tickets,
            'segments': segments,
            'ticket_type': ticket_type,
            'status_choices': status_choices,
            'priority_scale': priority_scale,
        }
        return render(request, 'tickets/update_ticket.html', context=context)


@login_required
def get_all_tickets(request):
    user = request.user
    company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company
    # Filter projects based on company and user membership
    projects = Project.objects.filter(company=company, members=user)
    # Get all tickets associated with the filtered projects
    tickets = Ticket.objects.filter(segment__project__in=projects).order_by('-id')
    # Prepare a dictionary to hold active stages for each ticket
    tickets_with_active_stages = []
    for ticket in tickets:
        active_stages = ticket.stages.filter(ticketstage__active=True).distinct()
        tickets_with_active_stages.append({
            'ticket': ticket,
            'active_stages': active_stages
        })
    context = {
        'tickets_with_active_stages': tickets_with_active_stages
    }
    return render(request, 'tickets/ticket_list.html', context)

@csrf_exempt
def update_ticket_stage(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        old_stage_id = request.POST.get('old_stage_id')
        new_stage_id = request.POST.get('new_stage_id')
        
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            old_stage = Stage.objects.get(id=old_stage_id)
            new_stage = Stage.objects.get(id=new_stage_id)
            # Deactivate all old stages for the ticket
            TicketStage.objects.filter(ticket=ticket, active=True).update(active=False)
            # Activate the new stage
            TicketStage.objects.update_or_create(
                ticket=ticket,
                stage=new_stage,
                defaults={'active': True}
            )
            # Retrieve the title of the newly activated stage
            new_stage_title = new_stage.title
            old_stage_title = old_stage.title
            return JsonResponse({
                'success': True,
                'ticket': {
                    'company_ticket_counter': ticket.company_ticket_counter,
                },
                'new_stage_title': new_stage_title,
                'old_stage_title': old_stage_title
            })
        except Ticket.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ticket not found.'})
        except Stage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Stage not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def fetch_segments(request):
    project_id = request.GET.get('project_id')
    segments = Segment.objects.filter(project__id=project_id).values('id', 'title')
    return JsonResponse({'segments': list(segments)})


def fetch_tickets_and_stages(request):
    segment_id = request.GET.get('segment_id')
    project_id = request.GET.get('project_id')
    if segment_id:
        tickets = Ticket.objects.filter(segment__id=segment_id).order_by('-id')
    else:
        tickets = Ticket.objects.filter(segment__project__id=project_id).order_by('-id')
    stages = Stage.objects.filter(ticketstage__ticket__in=tickets, ticketstage__active=True).distinct().order_by('id')
    tickets_data = {}
    for stage in stages:
        tickets_in_stage = tickets.filter(stages=stage)
        tickets_data[stage.id] = [
            {
                'id': ticket.id,
                'title': ticket.title,
                'company_ticket_counter': ticket.company_ticket_counter,
                'ticket_type': ticket.ticket_type,  # Numeric code
                'ticket_type_display': ticket.get_ticket_type_display()  # Human-readable name
            }
            for ticket in tickets_in_stage
        ]

    response_data = {
        'stages': list(stages.values('id', 'title')),  # Basic stage info
        'tickets': tickets_data
    }

    return JsonResponse(response_data)

@login_required
def kanban_board(request):

    user = request.user
    company = CustomerCompanyDetails.objects.filter(company_root_user=user).first().company

    # Filter tickets based on projects where user is a member.
    # projects = Project.objects.filter(company=company, members=user) 
    # Currently fetching all projects where he can see all segments and tickets since everyone is contributor. 
    # this will not be a problem later.
    projects = Project.objects.filter(company=company)
    stages = Stage.objects.filter(company=company)
    stage_status_choices = STAGE_STATUS_CHOICES
    

    context = {
        'projects': projects,
        'stage_status_choices': stage_status_choices,
        'stages': stages
    }
    return render(request, 'tickets/kanban_board.html', context)

