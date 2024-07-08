from django.urls import path
from . import views

app_name = "sprints"

"""
list of all possible tasks for sprints

create sprint
delete sprint
update sprint
get sprint
get all or specific sprints
activate all or specific sprints
deactivate all or specific sprints
get active sprints
get deactive sprints
show sprint history for a particular sprint if possible
For all list data table views, need to do bulk update option.
For all list data table views, need to do bulk update option. Need to write get views based on permissions. Add all possible filters seperately for each field. Not a common search bar.

"""

urlpatterns = [
    path('create_sprint/', views.create_sprint, name="create_sprint"),
    # path('sprint/<int:sprint_id>/', views.get_sprint, name="sprint"),
    path('update_sprint/<int:sprint_id>/', views.update_sprint, name="update_sprint"),
    # path('delete_sprint/<int:sprint_id>/', views.delete_sprint, name="delete_sprint"),
    path('sprints/', views.get_all_sprints, name="sprint_list"),
    
    # path('create_sprint_for_ticket/', views.CreateTicketSprintView.as_view(), name="create_sprint_for_ticket"),
    # path('create_sprint_for_phase/', views.CreatePhaseSprintView.as_view(), name="create_sprint_for_phase"),
    # path('create_sprint_for_project/', views.CreateProjectSprintView.as_view(), name="create_sprint_for_project"),
    # path('create_sprint_for_segment/', views.CreateSegmentSprintView.as_view(), name="create_sprint_for_segment"),
    # path('sprint/<int:sprint_id>/<str:input_list>/', views.SprintView.as_view(), name="sprint"),
    # path('get_sprints/<str:sprint_ids>/', views.GetSprintsView.as_view(), name="get_sprints"),
    # path('activate_sprints/<str:sprint_ids>/', views.ActivateSprints.as_view(), name="activate_sprints"),
    # path('deactivate_sprints/<str:sprint_ids>/', views.DeActivateSprints.as_view(), name="deactivate_sprints"),
    # path('get_active_sprints/', views.GetActiveSprintsView.as_view(), name="get_active_sprints"),
    # path('get_deactive_sprints/', views.GetDeActiveSprintsView.as_view(), name="get_Deactive_sprints"),
    # path('get_sprint_history/<int:sprint_id>/', views.GetSprintHistoryView.as_view(), name="get_sprint_history"),
]