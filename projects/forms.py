from django import forms
from .models import Project, ProjectPhase, ProjectAssignment
from django.core.exceptions import ValidationError

class ProjectForm(forms.ModelForm):
    def clean_title(self):
        title = self.cleaned_data['title']
        if Project.objects.filter(title=title).exists():
            raise ValidationError("Title must be unique.")
        return title
    class Meta:
        model = Project
        fields = ['title', 'description', 'start_date', 'end_date', 'status', 'company', 'members', 'created_by', 'updated_by']
        widgets = {
                    'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
                }
        error_messages = {
            'title': {
                'unique': "This title already exists. Please choose a unique title."
            }
        }
class ProjectPhaseForm(forms.ModelForm):
    class Meta:
        model = ProjectPhase
        fields = ['phase', 'status']

class ProjectAssignmentForm(forms.ModelForm):
    class Meta:
        model = ProjectAssignment
        fields = ['assigned_by', 'assigned_to']