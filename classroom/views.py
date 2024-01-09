from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Enrollment, Classroom

# Create your views here.
def activeClasses(request):
    enrollments = Enrollment.objects.filter(student=request.user, status__in=["training", "testing"])
    classrooms = [enrollment.classroom for enrollment in enrollments]
    return render(request, 'core/classes/student-classes-partial.html', {'classes': classrooms})

def completedClasses(request):
    enrollments = Enrollment.objects.filter(student=request.user, status="completed")
    classrooms = [enrollment.classroom for enrollment in enrollments]
    return render(request, 'core/classes/student-classes-partial.html', {'classes': classrooms})

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
