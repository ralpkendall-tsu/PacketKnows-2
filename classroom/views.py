from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render

from activity.models import Activity, Course, BaseActivity
from .models import Enrollment, Classroom
from django.db.models import Avg
from django.db.models.functions import Coalesce
from activity.views import computeClassStrengthRating, compute_student_rank, computeClassRanks
import random
import string
from django.core.files.uploadedfile import SimpleUploadedFile
from activity.views import computeTrainingProgressReport, computeTestingProgressReport
from user.models import CustomUser

# Create your views here.
def activeClasses(request):
    enrollments = Enrollment.objects.filter(student=request.user, status__in=["training", "testing"])
    classrooms = [enrollment.classroom for enrollment in enrollments]
    return render(request, 'core/classes/student-classes-partial.html', {'classes': classrooms})

def completedClasses(request):
    enrollments = Enrollment.objects.filter(student=request.user, status="completed")
    classrooms = [enrollment.classroom for enrollment in enrollments]
    return render(request, 'core/classes/student-classes-partial.html', {'classes': classrooms})

def allClasses(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    classrooms = [enrollment.classroom for enrollment in enrollments]
    return render(request, 'core/classes/selfLearner-classes-partial.html', {'classes': classrooms})

def Classes(request):
    if request.method == 'POST':
        classCode = request.POST.get('classCode')
        if classCode:
            try:
                classroom = Classroom.objects.get(code=classCode)
            except Classroom.DoesNotExist:
                return JsonResponse({'message': 'Invalid class code. Class not found.'}, status=404)

            if Enrollment.objects.filter(student=request.user, classroom=classroom).exists():
                return JsonResponse({'message': 'You are already enrolled in this class.'}, status=200)

            enrollment = Enrollment.objects.create(student=request.user, classroom=classroom)
            return JsonResponse({'message': 'Successfully enrolled in the class.'}, status=200)
        else:
            return JsonResponse({'message': 'Class code is required.'}, status=400)
    else:
        return JsonResponse({'message': 'Invalid request method.'}, status=400)
    
def ClassroomView(request, id):
    if request.method == "DELETE":
        enrollment = get_object_or_404(Enrollment, classroom_id=id, student=request.user)
        enrollment.delete()
        return JsonResponse({'message': 'Successfully left the class.'}, status=200)
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({'message': 'Invalid request method.'}, status=400)

def ClassOverAllFeedbackView(request):
    context = {}
    if request.method == "POST":
        pass
    else:
        classID = request.GET.get('classroomID')

        classroom = Classroom.objects.get(id=classID)
        strengthRating = computeClassStrengthRating(student=request.user,classroom=classroom)

        feedback = {}
        feedback["bestCategory"] = strengthRating[0].get("name")
        feedback["worstCategory"] = strengthRating[-1].get("name")
        feedback["classRank"] = compute_student_rank(request.user, classroom)

        context['feedback'] = feedback

    return render(request, 'core/dashboards/student-dashboard-feedback-partial.html', context)

def TopPerformingStudentsView(request):
    context = {}
    if request.method == "POST":
        pass
    else:
        classID = request.GET.get("classroomID")
        classroom = Classroom.objects.get(id=classID)
        context["classRank"] = computeClassRanks(classroom=classroom)
        print(context["classRank"])

    return render(request, 'core/dashboards/instructor-dashboard-topStudents-partial.html', context)

def InstructorClassesView(request, status):
    context= {}
    if request.method == "POST":
        pass
    else:
        classrooms = []
        if status == "active":    
            classrooms = Classroom.objects.filter(instructor=request.user, is_active=True)
        elif status == "archived":
            classrooms = Classroom.objects.filter(instructor=request.user, is_active=False)
        elif status == "all":
            classrooms = Classroom.objects.filter(instructor=request.user)
            
        context["classes"] = classrooms
    
    return render(request, 'core/classes/instructor-classes-partial.html', context)

def CreateClassView(request):
    if request.method == "POST":
        section = request.POST.get("section")
        school_year = request.POST.get("year")
        courseID = request.POST.get("courseID")
        course = Course.objects.get(id=courseID)
        
        # name
        instructor = request.user
        first_name_initials = ''.join([word[0].upper() for word in instructor.first_name.split()])
        last_name = instructor.last_name
        name = f"{first_name_initials}{last_name}_{course.slug}_{section}_{school_year}"
        print(name)
        
        # code
        code = generate_random_code()
        code = name + "_" + code
        while Classroom.objects.filter(code=code).exists():
            code = generate_random_code()
            code = name + "_" + code
        
        
        # description
        description = course.description
        
        # icon
        random_num = random.randint(1, 10)
        file_path = f'media/classroom/class-icons/templates/{random_num}.jpg'
        with open(file_path, 'rb') as image_file:
            image_data = image_file.read()
            
        icon = SimpleUploadedFile(name=f'{code}_{random_num}.jpg', content=image_data, content_type='image/jpeg')
        
        
        createdClass = Classroom.objects.create(
            name = name,
            code = code,
            description = description,
            icon = icon,
            section = section,
            school_year = school_year,
            instructor = instructor,
            course = course
        )
        
        
        response_data = {'message': 'Class created successfully'}
        return JsonResponse(response_data, status=200)
    
def generate_random_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def ClassDashboardView(request, classID):
    context={}
    if request.method == "POST":
        pass
    else:
        classroom = Classroom.objects.get(id=classID)
        context["classroom"] = classroom
        
        
        context["activityCount"] = BaseActivity.objects.filter(course=classroom.course).count()
        
        context["trainingCount"] = Enrollment.objects.filter(classroom=classroom, status="training").count()
        context["testingCount"] = Enrollment.objects.filter(classroom=classroom, status="testing").count()
        context["completedCount"] = Enrollment.objects.filter(classroom=classroom, status="completed").count()
        
        studentDatas = []
        students = classroom.students.all()
        for student in students:
            studentData = {}
            studentData["id"] = student.id
            studentData["name"] = f"{student.first_name} {student.last_name}"
            
            # current mode
            enrollment = Enrollment.objects.get(student=student, classroom=classroom)
            studentData["currentMode"] = enrollment.status
            
            # training percentage
            studentData["trainingPercentage"] = computeTrainingProgressReport(student, classroom)["total_training_percentage"]
            # testing percentage
            studentData["testingPercentage"] = computeTestingProgressReport(student, classroom)["total_testing_percentage"]
            
            # append studentData to studentDatas
            studentDatas.append(studentData)
            
        context["studentDatas"] = studentDatas
        
        
        
    
    return render(request, 'core/classes/instructor-class-dashboard.html', context)

def ArchiveClassView(request, classID):
    try:
        classroom = Classroom.objects.get(id=classID)
        if classroom.is_active == False:
            classroom.is_active = True
            
        else:
            classroom.is_active = False
        
        classroom.save()

        if classroom.is_active == True:
            return JsonResponse({"message": "Class unarchived successfully"}, status=200)
        else:
            return JsonResponse({"message": "Class archived successfully"}, status=200)
    except Classroom.DoesNotExist:
        return JsonResponse({"message": "Class not found"}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"Error archiving class: {str(e)}"}, status=500)

def DeleteClassView(request, classID):
    try:
        classroom = Classroom.objects.get(id=classID)
        classroom.delete()

        return JsonResponse({"message": "Class deleted successfully"}, status=200)
    except Classroom.DoesNotExist:
        return JsonResponse({"message": "Class not found"}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"Error deleting class: {str(e)}"}, status=500)
    
def RemoveStudentView(request, classID, userID):
    try:
        classroom = Classroom.objects.get(id=classID)
        student = CustomUser.objects.get(id=userID)
        enrollment = Enrollment.objects.get(student=student, classroom=classroom)
        enrollment.delete()

        return JsonResponse({"message": "Student removed successfully"}, status=200)
    except Exception as e:
        return JsonResponse({"message": f"Error removing student: {str(e)}"}, status=500)
    
    
def GetStudentsView(request,classroomID, status):
    context = {}
    if request.method == "POST":
        pass
    else:
        studentDatas = []
        classroom = Classroom.objects.get(id=classroomID)
        context["classroom"] = classroom
        students = classroom.students.filter(enrollment__status=status)
        
        for student in students:
            studentData = {}
            studentData["id"] = student.id
            studentData["name"] = f"{student.first_name} {student.last_name}"
            
            # current mode
            enrollment = Enrollment.objects.get(student=student, classroom=classroom)
            studentData["currentMode"] = enrollment.status
            
            # training percentage
            studentData["trainingPercentage"] = computeTrainingProgressReport(student, classroom)["total_training_percentage"]
            # testing percentage
            studentData["testingPercentage"] = computeTestingProgressReport(student, classroom)["total_testing_percentage"]
            
            # append studentData to studentDatas
            studentDatas.append(studentData)
            
        context["studentDatas"] = studentDatas
        
    return render(request, 'core/classes/instructor-class-dashboard-student-partial.html', context)
    