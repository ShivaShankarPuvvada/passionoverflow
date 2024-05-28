from django.shortcuts import render

def home_page(request):
    return render(request, 'home_page.html')


def about_us(request):
    return render(request, 'about_us.html')

def why_choose_us(request):
    return render(request, 'why_choose_us.html')

def pricing(request):
    return render(request, 'pricing.html')