from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home_page(request):
    return render(request, 'home_page.html')


def about_us(request):
    return render(request, 'about_us.html')

def why_choose_us(request):
    return render(request, 'why_choose_us.html')

def pricing(request):
    return render(request, 'pricing.html')

@login_required
def docs(request):
    return render(request, 'docs.html')

@login_required
def contact_us(request):
    return render(request, 'contact_us.html')
