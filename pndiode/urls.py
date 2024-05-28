"""
URL configuration for pndiode project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home_page'),
    path('about_us/', views.about_us, name='about_us'),
    path('why_choose_us/', views.why_choose_us, name='why_choose_us'),
    path('pricing/', views.pricing, name='pricing'),
    path('accounts/', include('accounts.urls')),
    path('phases/', include('phases.urls')),
    path('projects/', include('projects.urls')),
    path('segments/', include('segments.urls')),
    path('stages/', include('stages.urls')),
    path('tags/', include('tags.urls')),
    path('tickets/', include('tickets.urls')),
    path('sprints/', include('sprints.urls')),
    path('milestones/', include('milestones.urls')),
]
