from django.urls import path
from . import views

app_name = "milestones"

"""
list of all possible tasks for milestones

create milestone
delete milestone
update milestone
get milestone
get all or specific milestones
activate all or specific milestones
deactivate all or specific milestones
get active milestones
get deactive milestones
show milestone history for a particular milestone if possible
For all list data table views, need to do bulk update option. Need to write get views based on permissions. Add all possible filters seperately for each field. Not a common search bar.

"""

urlpatterns = [
    path('create_milestone/', views.create_milestone, name="create_milestone"),
    # path('milestone/<int:milestone_id>/', views.get_milestone, name="milestone"),
    path('update_milestone/<int:milestone_id>/', views.update_milestone, name="update_milestone"),
    # path('delete_milestone/<int:milestone_id>/', views.delete_milestone, name="delete_milestone"),
    path('milestones/', views.get_all_milestones, name="milestone_list"),
    path('validate-segment-project/', views.validate_segment_project, name='validate_segment_project'),
    path('ajax/get-segments/', views.get_segments_by_project, name='get_segments_by_project'),
    path('get-project-by-segment/', views.get_project_by_segment, name='get_project_by_segment'),
    path('milestones-calendar/', views.get_all_milestones_in_calendar, name="milestone_calendar"),
    path('milestones-pipeline/', views.get_all_milestones_in_pipeline, name="milestone_pipeline"),

    # path('create_milestone/', views.CreateMilestoneView.as_view(), name="create_milestone"),
    # path('milestone/<int:milestone_id>/', views.MilestoneView.as_view(), name="milestone"),
    # path('get_milestones/<str:milestone_ids>/', views.GetMilestonesView.as_view(), name="get_milestones"),
    # path('activate_milestones/<str:milestone_ids>/', views.ActivateMilestones.as_view(), name="activate_milestones"),
    # path('deactivate_milestones/<str:milestone_ids>/', views.DeActivateMilestones.as_view(), name="deactivate_milestones"),
    # path('get_active_milestones/', views.GetActiveMilestonesView.as_view(), name="get_active_milestones"),
    # path('get_deactive_milestones/', views.GetDeActiveMilestonesView.as_view(), name="get_Deactive_milestones"),
    # path('get_project_milestones/<int:project_id>/', views.GetProjectMilestonesView.as_view(), name="get_project_milestones"),
    # path('get_segment_milestones/<int:segment_id>/', views.GetSegmentMilestonesView.as_view(), name="get_segment_milestones"),
    # path('get_milestone_history/<int:milestone_id>/', views.GetMilestoneHistoryView.as_view(), name="get_milestone_history"),
]