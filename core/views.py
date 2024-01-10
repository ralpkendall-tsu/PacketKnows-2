
import json
from django.shortcuts import get_object_or_404, render
from user.forms import CustomUserForm
from user.forms import CustomLoginForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from classroom.models import Classroom, Enrollment
from activity.views import computeTrainingProgressReport, computeTestingProgressReport, computeOverallStrengthRating, computeAverageClassProgress, computeSingleActivityScore
from activity.models import Activity, Course
from help.models import TestReactivation, Notification
from user.models import CustomUser

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
        userCategory = request.user.category.name
        if userCategory == "Student":
            student = request.user
            context["notifications"] = Notification.objects.filter(receiver=student)
            
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
        elif userCategory == "Instructor":
            classrooms = Classroom.objects.filter(instructor=request.user)
            context["classrooms"] = classrooms
            
            enrollments = Enrollment.objects.filter(classroom__in=classrooms)
            context["allStudentCount"] = enrollments.count()
            
            context["testReactivations"] =  TestReactivation.objects.filter(classroom__instructor=request.user)
            

    return render(request, 'core/dashboard.html', context)

@login_required(login_url='/')
def ClassesView(request):
    context = {}
    if request.method == 'POST':
        pass
    else:
        userCategory = request.user.category.name
        if userCategory == "Student":
            pass
        elif userCategory == "Instructor":
            courses = Course.objects.all()
            context["courses"] = courses
        elif userCategory == "Self Learner":
            pass
        
    return render(request, 'core/classes.html', context)

@login_required(login_url='/')
def SettingsView(request):
    context = {}
    if request.method == 'POST':
        pass
    else:
        userCategory = request.user.category.name
        if userCategory == "Student":
            pass
        elif userCategory == "Instructor":
            pass
        elif userCategory == "Self Learner":
            pass

    return render(request, 'core/settings.html', context)

@login_required(login_url='/')
def HelpView(request):
    context = {}
    if request.method == 'POST':
        pass
    else:
        userCategory = request.user.category.name
        if userCategory == "Student":
            enrollments = Enrollment.objects.filter(student=request.user)
            classrooms = [enrollment.classroom for enrollment in enrollments]
            
            context["classrooms"] = classrooms
        elif userCategory == "Instructor":
            context["testReactivations"] =  TestReactivation.objects.filter(classroom__instructor=request.user)
        elif userCategory == "Self Learner":
            pass
        
    return render(request, 'core/help.html', context)

@login_required(login_url='/')
def ProgressReportTrainingView(request, classSlug):
    context = {}
    if request.method == 'POST':
        pass
    else:
        userCategory = request.user.category.name
        if userCategory == "Student":
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
        elif userCategory == "Instructor":
            pass
        elif userCategory == "Self Learner":
            pass
        
        

    return render(request, 'core/progress-report-training.html', context)

@login_required(login_url='/')
def ProgressReportTestingView(request, classSlug):
    context = {}
    if request.method == 'POST':
        pass
    else:
        userCategory = request.user.category.name
        if userCategory == "Student":
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
        elif userCategory == "Instructor":
            pass
        elif userCategory == "Self Learner":
            pass
        
        
        
    return render(request, 'core/progress-report-testing.html', context)

@login_required(login_url='/')
def ProgressReportTrainingInstructorView(request, classSlug, userID):
    context = {}
    if request.method == 'POST':
        pass
    else:
        student = CustomUser.objects.get(id=userID)
        context["student"] = student
        userCategory = student.category.name
        if userCategory == "Student":
            classroom = Classroom.objects.get(code=classSlug)
            context["classroom"] = classroom
            context["grades"] = computeTrainingProgressReport(student, classroom)
            
            
            enrollment = get_object_or_404(Enrollment, student=student, classroom=classroom)
            firstActivity = enrollment.activities.get(base_activity__number="1.1", mode="training")
            firstActivityScore = computeSingleActivityScore(student, firstActivity.id)
            bar_chart_labels = firstActivityScore['labels']
            bar_chart_data = firstActivityScore['data']
            
            context["barChartLabels"] = json.dumps(bar_chart_labels)
            context["barChartData"] = json.dumps(bar_chart_data)
            
            enrollment = get_object_or_404(Enrollment, student=student, classroom=classroom)
            enrollment.date_updated = timezone.now()
            enrollment.save()
        
    return render(request, 'core/progress-report-training.html', context)

@login_required(login_url='/')
def ProgressReportTestingInstructorView(request, classSlug, userID):
    context = {}
    if request.method == 'POST':
        pass
    else:
        student = CustomUser.objects.get(id=userID)
        context["student"] = student
        userCategory = student.category.name
        if userCategory == "Student":
            classroom = Classroom.objects.get(code=classSlug)
            context["classroom"] = classroom
            context["grades"] = computeTestingProgressReport(student, classroom)
            
            
            enrollment = get_object_or_404(Enrollment, student=student, classroom=classroom)
            firstActivity = enrollment.activities.get(base_activity__number="1.1", mode="testing")
            firstActivityScore = computeSingleActivityScore(student, firstActivity.id)
            bar_chart_labels = firstActivityScore['labels']
            bar_chart_data = firstActivityScore['data']
            
            context["barChartLabels"] = json.dumps(bar_chart_labels)
            context["barChartData"] = json.dumps(bar_chart_data)
            
            enrollment = get_object_or_404(Enrollment, student=student, classroom=classroom)
            enrollment.date_updated = timezone.now()
            enrollment.save()
        
    return render(request, 'core/progress-report-testing.html', context)

@login_required(login_url='/')
def ExamListView(request, classSlug, mode):
    context = {}
    
    if request.method == 'POST':
        pass
    else:
        userCategory = request.user.category.name
        if userCategory == "Student":
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
        elif userCategory == "Instructor":
            pass
        elif userCategory == "Self Learner":
            pass
        
        
            
    return render(request, 'core/exam-list.html', context)

def ActivitySimulationView(request, id, mode):
    context = {}
    
    if request.method == 'POST':
        pass
    else:
        userCategory = request.user.category.name
        if userCategory == "Student":
            activity = Activity.objects.get(id=id)
            context["activity"] = activity
        elif userCategory == "Instructor":
            pass
        elif userCategory == "Self Learner":
            pass
        
        
            
    return render(request, 'core/activity.html', context)