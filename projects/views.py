from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Project, ProjectPhase, ProjectAssignment
from .forms import ProjectForm, ProjectPhaseForm, ProjectAssignmentForm
from django.contrib.auth.decorators import login_required



@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.save()

            # Create related ProjectPhase records
            for phase_data in form.cleaned_data['phases']:
                phase = ProjectPhase.objects.create(project=project, **phase_data)

            # Create related ProjectAssignment records
            for user in form.cleaned_data['assigned_to']:
                assignment = ProjectAssignment.objects.create(project=project, assigned_to=user)

            return redirect('projects:project_list')
    else:
        form = ProjectForm()
    return render(request, 'projects/create_project.html', {'form': form})


@login_required
def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects:project', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/update_project.html', {'form': form, 'project': project})


@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        project.delete()
        return redirect('projects:project_list')
    return render(request, 'projects/delete_project.html', {'project': project})


@login_required
def get_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'projects/project_detail.html', {'project': project})


@login_required
def get_all_projects(request):
    projects = Project.objects.all()
    return render(request, 'projects/project_list.html', {'projects': projects})


@login_required
def change_project_status(request, project_ids, status):
    project_ids = project_ids.split(',')
    projects = Project.objects.filter(id__in=project_ids)
    projects.update(status=status)
    return redirect('projects:project_list')


@login_required
def open_projects(request, project_ids):
    return change_project_status(request, project_ids, "1")


@login_required
def close_projects(request, project_ids):
    return change_project_status(request, project_ids, "0")


@login_required
def project_phase_history(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    phases = project.phases.all()
    return render(request, 'projects/project_phase_history.html', {'project': project, 'phases': phases})


@login_required
def project_assignment_history(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    assignments = project.assignment_history.all()
    return render(request, 'projects/project_assignment_history.html', {'project': project, 'assignments': assignments})


@login_required
def project_history(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    history = project.history.all()
    return render(request, 'projects/project_history.html', {'project': project, 'history': history})


@login_required
def create_project_phase(request, project_id):
    if request.method == 'POST':
        form = ProjectPhaseForm(request.POST)
        if form.is_valid():
            project_phase = form.save(commit=False)
            project_phase.project_id = project_id
            project_phase.save()
            return redirect('projects:project_phase_history', project_id=project_id)
    else:
        form = ProjectPhaseForm()
    return render(request, 'projects/create_project_phase.html', {'form': form})


@login_required
def update_project_phase(request, project_id, phase_id):
    project_phase = get_object_or_404(ProjectPhase, project_id=project_id, id=phase_id)
    if request.method == 'POST':
        form = ProjectPhaseForm(request.POST, instance=project_phase)
        if form.is_valid():
            form.save()
            return redirect('projects:project_phase_history', project_id=project_id)
    else:
        form = ProjectPhaseForm(instance=project_phase)
    return render(request, 'projects/update_project_phase.html', {'form': form, 'project_phase': project_phase})


@login_required
def delete_project_phase(request, project_id, phase_id):
    project_phase = get_object_or_404(ProjectPhase, project_id=project_id, id=phase_id)
    if request.method == 'POST':
        project_phase.delete()
        return redirect('projects:project_phase_history', project_id=project_id)
    return render(request, 'projects/delete_project_phase.html', {'project_phase': project_phase})


@login_required
def create_project_assignment(request, project_id):
    if request.method == 'POST':
        form = ProjectAssignmentForm(request.POST)
        if form.is_valid():
            project_assignment = form.save(commit=False)
            project_assignment.project_id = project_id
            project_assignment.save()
            return redirect('projects:project_assignment_history', project_id=project_id)
    else:
        form = ProjectAssignmentForm()
    return render(request, 'projects/create_project_assignment.html', {'form': form})


@login_required
def update_project_assignment(request, project_id, assignment_id):
    project_assignment = get_object_or_404(ProjectAssignment, project_id=project_id, id=assignment_id)
    if request.method == 'POST':
        form = ProjectAssignmentForm(request.POST, instance=project_assignment)
        if form.is_valid():
            form.save()
            return redirect('projects:project_assignment_history', project_id=project_id)
    else:
        form = ProjectAssignmentForm(instance=project_assignment)
    return render(request, 'projects/update_project_assignment.html', {'form': form, 'project_assignment': project_assignment})


@login_required
def delete_project_assignment(request, project_id, assignment_id):
    project_assignment = get_object_or_404(ProjectAssignment, project_id=project_id, id=assignment_id)
    if request.method == 'POST':
        project_assignment.delete()
        return redirect('projects:project_assignment_history', project_id=project_id)
    return render(request, 'projects/delete_project_assignment.html', {'project_assignment': project_assignment})
