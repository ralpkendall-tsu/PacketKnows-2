from django.shortcuts import render
from user.forms import CustomUserForm
from user.forms import CustomLoginForm
from django.contrib.auth.decorators import login_required

# Create your views here.
def LandingPageView(request):
    context = {}
    if request.method == 'POST':
        pass
    else:
        context['loginForm'] = CustomLoginForm
        context['signupForm'] = CustomUserForm

    return render(request, 'core/landing-page.html', context)

@login_required(login_url='/')
def DashboardView(request):
    context = {}
    if request.method == 'POST':
        pass

    return render(request, 'core/dashboard.html', context)

@login_required(login_url='/')
def ClassesView(request):
    context = {}
    if request.method == 'POST':
        pass
    else:
        pass

    return render(request, 'core/classes.html', context)

@login_required(login_url='/')
def SettingsView(request):
    context = {}
    if request.method == 'POST':
        pass
    else:
        pass

    return render(request, 'core/settings.html', context)

@login_required(login_url='/')
def HelpView(request):
    context = {}
    if request.method == 'POST':
        pass
    else:
        pass

    return render(request, 'core/help.html', context)