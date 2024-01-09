from django.shortcuts import render
from user.forms import CustomUserForm
from user.forms import CustomLoginForm
from django.contrib.auth.decorators import login_required
from classroom.models import Classroom, Enrollment
from activity.views import computeTrainingProgressReport, computeTestingProgressReport, computeOverallStrengthRating
from activity.models import Activity

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
    else:
        context["strengthRating"] = computeOverallStrengthRating(request.user)

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

@login_required(login_url='/')
def ProgressReportTrainingView(request, classSlug):
    context = {}
    if request.method == 'POST':
        pass
    else:
        classroom = Classroom.objects.get(code=classSlug)
        context["classroom"] = classroom
        context["grades"] = computeTrainingProgressReport(request.user, classroom)
        

    return render(request, 'core/progress-report-training.html', context)

@login_required(login_url='/')
def ProgressReportTestingView(request, classSlug):
    context = {}
    if request.method == 'POST':
        pass
    else:
        classroom = Classroom.objects.get(code=classSlug)
        context["classroom"] = classroom
        context["grades"] = computeTestingProgressReport(request.user, classroom)
        
    return render(request, 'core/progress-report-testing.html', context)

@login_required(login_url='/')
def ExamListView(request, classSlug, mode):
    context = {}
    
    if request.method == 'POST':
        pass
    else:
        try:
            classroom = Classroom.objects.get(code=classSlug)
            enrollment = Enrollment.objects.get(student=request.user, classroom=classroom)
            activities = enrollment.activities.filter(mode=mode)
            context["activities"] = activities
            context["mode"] = mode
            context["course"] = classroom.course
            
        except (Classroom.DoesNotExist, Enrollment.DoesNotExist):
            context["error_message"] = "Classroom or enrollment not found."
            
    return render(request, 'core/exam-list.html', context)

def ActivitySimulationView(request, id, mode):
    context = {}
    
    if request.method == 'POST':
        pass
    else:
        activity = Activity.objects.get(id=id)
        context["activity"] = activity
            
    return render(request, 'core/activity.html', context)