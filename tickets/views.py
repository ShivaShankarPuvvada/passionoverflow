from .models import Ticket
from django.db.models import Q
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.decorators import login_required


@login_required
def create_ticket(request):
    
    """
    get method is not needed. we don't need to send anything to frontend.
    """
    if request.method == "POST":
        try:
            data = request.data
            must_keys = ["title", "start_date", "end_date"]
            
            if bool(set(must_keys) - set(data.keys())):
                return JsonResponse({'Message': str(set(must_keys) - set(data.keys())) + " missing"}, status=HTTPStatus.BAD_REQUEST)

            # Extract user data
            ticket_data = {
                "title": data["title"],
                "description": data["description"],
                "start_date": data["start_date"],
                "end_date": data["end_date"],
                "estimated_end_date": data["estimated_end_date"],
                "due_date": data["due_date"],
                "status": data["status"],
                "priority_type": data["priority_type"],
                "priority": data["priority"],
                "priority_scale": data["priority_scale"],
                "ticket_type": data["ticket_type"],
                "deleted": data["deleted"],
            }


            # Create User and Company instances
            ticket_object = Ticket(**ticket_data)
            # Validate and save User and Company instances
            ticket_object.save()

            response_data = {
                'data': ticket_object.data,
                "message": "Data Saved Successfully.",
            }
            
            return JsonResponse(response_data, status=HTTPStatus.CREATED)
        except Exception as error:
            error_message = "Internal Server Error: " + str(error)
            return JsonResponse({'Message': error_message}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        
@login_required
def get_active_tickets(request):
    
    if request.method == "GET":
        try:
            
            ticket_object = Ticket.objects.filter()

            if ticket_object.exists():
                ticket_object = ticket_object.latest()
                ticket_title = ticket_object.title
                ticket_description = ticket_object.description
                ticket_startdate = ticket_object.start_date
                ticket_enddate = ticket_object.end_date
                ticket_status = ticket_object.status
                ticket_priority = ticket_object.priority
                ticket_ticket_type = ticket_object.ticket_type
                response_data = {
                    'data': {
                        "ticket_title": ticket_title,
                        "ticket_description": ticket_description,
                        "ticket_startdate": ticket_startdate,
                        "ticket_enddate": ticket_enddate,
                        "ticket_status": ticket_status,
                        "ticket_priority": ticket_priority,
                        "ticket_ticket_type": ticket_ticket_type,
                        },
                }
                return JsonResponse(response_data, status=HTTPStatus.OK)
            else:
                response_data = {
                    'data': {
                        "proceed": True,
                        },
                    "message": "There are no tickets available",
                }
                return JsonResponse(response_data, status=HTTPStatus.OK)
        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return JsonResponse({'Message': error_message }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


@login_required
def ticket_view(request):
    
    if request.method == "POST":
        try:
            data=request.data
            must_keys=["id"]
            if bool(set(must_keys)-set(data.keys())):
                return JsonResponse({'Message':str(set(must_keys)-set(data.keys()))+" missing"}, status=HTTPStatus.BAD_REQUEST)
            
            ticket_id = data.get('id')
            ticket_object = Ticket.objects.filter(Q(id=ticket_id))

            if ticket_object.exists():
                ticket_object = ticket_object.latest()
                ticket_title = ticket_object.title
                ticket_description = ticket_object.description
                ticket_startdate = ticket_object.start_date
                ticket_enddate = ticket_object.end_date
                ticket_status = ticket_object.status
                ticket_priority = ticket_object.priority
                ticket_ticket_type = ticket_object.ticket_type
                response_data = {
                    'data': {
                        "ticket_title": ticket_title,
                        "ticket_description": ticket_description,
                        "ticket_startdate": ticket_startdate,
                        "ticket_enddate": ticket_enddate,
                        "ticket_status": ticket_status,
                        "ticket_priority": ticket_priority,
                        "ticket_ticket_type": ticket_ticket_type,
                        },
                }
                return JsonResponse(response_data, status=HTTPStatus.OK)
            else:
                response_data = {
                    'data': {
                        "proceed": True,
                        },
                    "message": "This is new data. We can proceed.",
                }
                return JsonResponse(response_data, status=HTTPStatus.OK)

        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return JsonResponse({'Message': error_message }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
