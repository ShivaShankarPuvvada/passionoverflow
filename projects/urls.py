from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    # path('create_project/', views.CreateProjectView.as_view(), name="create_project"),
    # path('project/', views.ProjectView.as_view(), name="project"),
]


# create project
# delete project
# update project
# get single project
# get all projects
# get only specific projects
# add persons to the project
# remove persons to the project
# add phase to the project (have to create phase apis, crud operations for phases)
# remove/detach phase to the project
# show phase history for a particular project (added this phase, deleted this phase on this date, added this phase on a particular date, current phase)
