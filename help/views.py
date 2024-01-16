from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.shortcuts import render
from classroom.models import Classroom
from user.models import CustomUser
from .models import StudentIDChange, TestReactivation, Notification
from activity.models import Activity

# Create your views here.
def ChangePassword(request):
    if request.method == 'POST':
        userEmail = request.user.email
        oldPassword = request.POST.get('oldPassword')
        newPassword = request.POST.get('newPassword')
        confirmPassword = request.POST.get('confirmPassword')
        
        user = CustomUser.objects.get(email=userEmail)
        
        if user:
            # Check if the old password matches
            if user.check_password(oldPassword):
                # Check if the new password and confirm password match
                if newPassword == confirmPassword:
                    # Change the password
                    user.set_password(newPassword)
                    user.save()
                    return JsonResponse({'success': True, 'message': 'Password changed successfully'})
                else:
                    return JsonResponse({'success': False, 'message': 'New password and confirm password do not match'})
            else:
                return JsonResponse({'success': False, 'message': 'Old password is incorrect'})
        else:
            return JsonResponse({'success': False, 'message': 'User not found'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def UpdateStudentNumber(request):
    if request.method == 'POST':
        newID = request.POST.get('newID')
        userEmail = request.user.email

        # Check if newID is composed of only numbers
        if not newID.isdigit():
            return JsonResponse({'success': False, 'message': 'Invalid newID. Please provide a numeric value.'})

        # Create a StudentIDChange record
        studentIDChange = StudentIDChange.objects.create(student=request.user, new_school_id=newID)

        return JsonResponse({'success': True, 'message': 'The admin has been notified. Please wait for it to reflect.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def TestReactivationView(request):
    if request.method == 'POST':
        try:
            activityID = request.POST.get("activityID")
            classID = request.POST.get("classroomID")
            message = request.POST.get("message")
            
            activity = Activity.objects.get(id=activityID)
            classroom = Classroom.objects.get(id=classID)
            testReactivation = TestReactivation.objects.create(student=request.user, classroom=classroom, activity=activity, message=message)

            return JsonResponse({"message": "Test reactivation created successfully"}, status=200)
        except Activity.DoesNotExist:
            return JsonResponse({"message": "Activity does not exist"}, status=400)
        except Exception as e:
            print(str(e))
            return JsonResponse({"message": str(e)}, status=500)
        
def ReactivateTestView(request, testReactivationID):
    if request.method == 'POST':
        try:
            testReactivation = TestReactivation.objects.get(id=testReactivationID)
            # reactivate the exam
            
            # delete the test reactivation record(testReactivation)
            testReactivation.delete()
            
            return JsonResponse({"message": "Test reactivated successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
def ClearAllNotificationsView(request):
    if request.method == 'DELETE':
        try:
            notifications = Notification.objects.filter(receiver=request.user)
            notifications.delete()
            
            return JsonResponse({"message": "Notifications cleared successfully"}, status=200)
        except Exception as e:
            print(str(e))
            return JsonResponse({"error": str(e)}, status=500)
        