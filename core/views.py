
import json
from django.shortcuts import get_object_or_404, render
from user.forms import CustomUserForm
from user.forms import CustomLoginForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from classroom.models import Classroom, Enrollment
from activity.views import computeTrainingProgressReport, computeTestingProgressReport, computeOverallStrengthRating, computeAverageClassProgress, computeSingleActivityScore
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
        enrollments = Enrollment.objects.filter(student=request.user)
        total_active_test_count = 0 
        for enrollment in enrollments:
            activities = enrollment.activities.filter(status="working")
            total_active_test_count += activities.count()
        
        ordered_enrollments = enrollments.order_by('-date_updated')
        classrooms = [enrollment.classroom for enrollment in ordered_enrollments]
        
        context["strengthRating"] = computeOverallStrengthRating(request.user)
        context["activeTestCount"] = total_active_test_count
        context["classes"] = classrooms
        
        # bar chart
        average_progress = computeAverageClassProgress(request.user, "training")
        
        bar_chart_labels = average_progress['class_names']
        bar_chart_data = average_progress['averages']
        
        context["barChartLabels"] = json.dumps(bar_chart_labels)
        context["barChartData"] = json.dumps(bar_chart_data)
        
        # feedback selection
        enrollments = Enrollment.objects.filter(student=request.user)
        classrooms = [enrollment.classroom for enrollment in enrollments]
        
        context["classrooms"] = classrooms

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
        enrollments = Enrollment.objects.filter(student=request.user)
        classrooms = [enrollment.classroom for enrollment in enrollments]
        
        context["classrooms"] = classrooms

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
        
        
        enrollment = get_object_or_404(Enrollment, student=request.user, classroom=classroom)
        firstActivity = enrollment.activities.get(base_activity__number="1.1", mode="training")
        firstActivityScore = computeSingleActivityScore(request.user, firstActivity.id)
        bar_chart_labels = firstActivityScore['labels']
        bar_chart_data = firstActivityScore['data']
        
        context["barChartLabels"] = json.dumps(bar_chart_labels)
        context["barChartData"] = json.dumps(bar_chart_data)
        
        enrollment = get_object_or_404(Enrollment, student=request.user, classroom=classroom)
        enrollment.date_updated = timezone.now()
        enrollment.save()

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
        
        
        enrollment = get_object_or_404(Enrollment, student=request.user, classroom=classroom)
        firstActivity = enrollment.activities.get(base_activity__number="1.1", mode="testing")
        firstActivityScore = computeSingleActivityScore(request.user, firstActivity.id)
        bar_chart_labels = firstActivityScore['labels']
        bar_chart_data = firstActivityScore['data']
        
        context["barChartLabels"] = json.dumps(bar_chart_labels)
        context["barChartData"] = json.dumps(bar_chart_data)
        
        enrollment = get_object_or_404(Enrollment, student=request.user, classroom=classroom)
        enrollment.date_updated = timezone.now()
        enrollment.save()
        
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
            
            enrollment = get_object_or_404(Enrollment, student=request.user, classroom=classroom)
            enrollment.date_updated = timezone.now()
            enrollment.save()
            
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