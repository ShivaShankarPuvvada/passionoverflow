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


New additional requirements, cover all these in a single or multiple views based on the requirement:
For all list data table views, need to do bulk update option.
For all list data table views, need to do bulk update option. Need to write get views based on permissions. Add all possible filters seperately for each field. Not a common search bar.

Get all tickets for contributor. It will fetch all tickets for the projects he involved in.
Get all tickets for a project if he is a member.
Get all tickets for a segment if he is a member.
Get all tickets for a stage in the segment if he is a member.
Get all tickets created by himself, the user or other guy by taking a user id or list of ids.
Get all tickets assigned to himself, the user or other guy by taking user id or list of ids.
Get all tickets by priority type.
Get all tickets by ticket type.
Get all tickets by status.
Add kanban board for tickets, ask chatgpt, it has unique way of doing it.
Show all the choice descriptions in the tickets create and update fields.
"""

urlpatterns = [
    path('create_ticket/', views.create_ticket, name="create_ticket"),
    path('update_ticket/<int:ticket_id>/', views.update_ticket, name="update_ticket"),
    path('tickets/', views.get_all_tickets, name="ticket_list"),
    path('kanban_board/', views.kanban_board, name="kanban_board"),

    # path('create_ticket/', views.create_ticket, name="create_ticket"),
    # path('ticket/<int:ticket_id>/', views.ticket_view, name="ticket"),
    # # path('get_tickets/<str:ticket_ids>/', views.GetTicketsView.as_view(), name="get_tickets"),
    # # path('activate_tickets/<str:ticket_ids>/', views.ActivateTickets.as_view(), name="activate_tickets"),
    # # path('deactivate_tickets/<str:ticket_ids>/', views.DeActivateTickets.as_view(), name="deactivate_tickets"),
    # path('get_active_tickets/', views.get_active_tickets, name="get_active_tickets"),
    # # path('get_deactive_tickets/', views.GetDeActiveTicketsView.as_view(), name="get_Deactive_tickets"),
    # # path('get_ticket_history/<int:ticket_id>/', views.GetTicketHistoryView.as_view(), name="get_ticket_history"),
]