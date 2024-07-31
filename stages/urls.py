from django.urls import path
from . import views

app_name = "stages"

"""
list of all possible tasks for stages

create stage
delete stage
update stage
get stage
get all or specific stages
activate all or specific stages
deactivate all or specific stages
get active stages
get deactive stages
show stage history for a particular stage if possible
For all list data table views, need to do bulk update option.
For all list data table views, need to do bulk update option. Need to write get views based on permissions. Add all possible filters seperately for each field. Not a common search bar.

"""

urlpatterns = [
    path('create_stage/', views.create_stage, name="create_stage"),
    path('create_stage_from_kanban/', views.create_stage_from_kanban, name="create_stage_from_kanban"),
    path('update_stage/<int:stage_id>/', views.update_stage, name="update_stage"),
    path('stages/', views.get_all_stages, name="stage_list"),

    # path('create_stage/', views.CreateStageView.as_view(), name="create_stage"),
    # path('stage/<int:stage_id>/', views.StageView.as_view(), name="stage"),
    # path('get_stages/<str:stage_ids>/', views.GetStagesView.as_view(), name="get_stages"),
    # path('activate_stages/<str:stage_ids>/', views.ActivateStages.as_view(), name="activate_stages"),
    # path('deactivate_stages/<str:stage_ids>/', views.DeActivateStages.as_view(), name="deactivate_stages"),
    # path('get_active_stages/', views.GetActiveStagesView.as_view(), name="get_active_stages"),
    # path('get_deactive_stages/', views.GetDeActiveStagesView.as_view(), name="get_Deactive_stages"),
    # path('get_stage_history/<int:stage_id>/', views.GetStageHistoryView.as_view(), name="get_stage_history"),
]