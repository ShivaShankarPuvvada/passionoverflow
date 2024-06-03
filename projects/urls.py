from django.urls import path
from . import views

app_name = "projects"


"""
list of all possible tasks for projects

# create project (by default project status = 1)
# delete project
# update project
# get project
# get all or specific projects
# close projects (change status to 0)
# open projects (change status to 1)
# add employees to the project (this will be covered in CRUD operations)
# remove employees to the project (this will be covered in CRUD operations)
# remove admim members to the project (this will be covered in CRUD operations)
# add/change phase to the project (this will be covered in CRUD operations)
# add admin members to the project (this will be covered in CRUD operations)
# project phase CRUD operations will be covered in Project model CRUD operations.
# Project assignment CRUD operations will be covered in Project model CRUD operations.
# show assignment history for a project (get all the rows for this project and display them in order)
# show phase history for a project (added this phase, deleted this phase on this date, added this phase on a particular date, current phase)
# show project model history if possible
"""

# urlpatterns = [
    # path('create_project/', views.CreateProjectView.as_view(), name="create_project"),
    # path('project/<int:project_id>/', views.ProjectView.as_view(), name="project"),
    # path('get_projects/<str:project_ids>/', views.GetProjectsView.as_view(), name="get_projects"),
    # path('open_projects/<str:project_ids>/', views.OpenProjectsView.as_view(), name="open_projects"),
    # path('close_projects/<str:project_ids>/', views.CloseProjectsView.as_view(), name="close_projects"),
    # path('project_phase_history/<int:project_id>/', views.ProjectPhaseHistoryView.as_view(), name="project_phase_history"),
    # path('project_assignment_history/<int:project_id>/', views.ProjectAssignmentHistoryView.as_view(), name="project_assignment_history"),
    # path('project_history/<int:project_id>/', views.ProjectHistoryView.as_view(), name="project_history"),
# ]

urlpatterns = [
    # Project URLs
    path('create_project/', views.create_project, name="create_project"),
    # path('project/<int:project_id>/', views.get_project, name="project"),
    # path('update_project/<int:project_id>/', views.update_project, name="update_project"),
    # path('delete_project/<int:project_id>/', views.delete_project, name="delete_project"),
    # path('projects/', views.get_all_projects, name="project_list"),
    # path('open_projects/<str:project_ids>/', views.open_projects, name="open_projects"),
    # path('close_projects/<str:project_ids>/', views.close_projects, name="close_projects"),
    # path('project_phase_history/<int:project_id>/', views.project_phase_history, name="project_phase_history"),
    # path('project_assignment_history/<int:project_id>/', views.project_assignment_history, name="project_assignment_history"),
    # path('project_history/<int:project_id>/', views.project_history, name="project_history"),

    # # Project Phase URLs
    # path('create_project_phase/<int:project_id>/', views.create_project_phase, name="create_project_phase"),
    # path('update_project_phase/<int:project_id>/<int:phase_id>/', views.update_project_phase, name="update_project_phase"),
    # path('delete_project_phase/<int:project_id>/<int:phase_id>/', views.delete_project_phase, name="delete_project_phase"),
    
    # # Project Assignment URLs
    # path('create_project_assignment/<int:project_id>/', views.create_project_assignment, name="create_project_assignment"),
    # path('update_project_assignment/<int:project_id>/<int:assignment_id>/', views.update_project_assignment, name="update_project_assignment"),
    # path('delete_project_assignment/<int:project_id>/<int:assignment_id>/', views.delete_project_assignment, name="delete_project_assignment"),
]
