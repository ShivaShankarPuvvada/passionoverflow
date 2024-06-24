from django.urls import path
from . import views

app_name = "tickets"

"""
list of all possible tasks for tickets

create ticket
delete ticket
update ticket
get ticket
get all or specific tickets
activate all or specific tickets
deactivate all or specific tickets
get active tickets
get deactive tickets
show ticket history for a particular ticket if possible
"""

urlpatterns = [
    path('create_ticket/', views.create_ticket, name="create_ticket"),
    path('ticket/<int:ticket_id>/', views.ticket_view, name="ticket"),
    # path('get_tickets/<str:ticket_ids>/', views.GetTicketsView.as_view(), name="get_tickets"),
    # path('activate_tickets/<str:ticket_ids>/', views.ActivateTickets.as_view(), name="activate_tickets"),
    # path('deactivate_tickets/<str:ticket_ids>/', views.DeActivateTickets.as_view(), name="deactivate_tickets"),
    path('get_active_tickets/', views.get_active_tickets, name="get_active_tickets"),
    # path('get_deactive_tickets/', views.GetDeActiveTicketsView.as_view(), name="get_Deactive_tickets"),
    # path('get_ticket_history/<int:ticket_id>/', views.GetTicketHistoryView.as_view(), name="get_ticket_history"),
]