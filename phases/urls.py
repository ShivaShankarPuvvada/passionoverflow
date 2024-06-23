from django.urls import path
from . import views

app_name = "phases"

"""
list of all possible tasks for phases

create phase
delete phase
update phase
get phase
get all or specific phases
activate all or specific phases
deactivate all or specific phases
get active phases
get deactive phases
show phase history for a particular phase if possible
"""

urlpatterns = [
    path('create_phase/', views.create_phase, name="create_phase"),
    path('update_phase/<int:phase_id>/', views.update_phase, name="update_phase"),
    path('phases/', views.get_all_phases, name="phase_list"),

    # path('phase/<int:phase_id>/', views.PhaseView.as_view(), name="phase"),
    # path('get_phases/<str:phase_ids>/', views.GetPhasesView.as_view(), name="get_phases"),
    # path('activate_phases/<str:phase_ids>/', views.ActivatePhases.as_view(), name="activate_phases"),
    # path('deactivate_phases/<str:phase_ids>/', views.DeActivatePhases.as_view(), name="deactivate_phases"),
    # path('get_active_phases/', views.GetActivePhasesView.as_view(), name="get_active_phases"),
    # path('get_deactive_phases/', views.GetDeActivePhasesView.as_view(), name="get_Deactive_phases"),
    # path('get_phase_history/<int:phase_id>/', views.GetPhaseHistoryView.as_view(), name="get_phase_history"),
]