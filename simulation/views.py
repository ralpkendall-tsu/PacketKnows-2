import json
from django.shortcuts import render
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.http import JsonResponse
from classroom.models import Enrollment
from user.models import CustomUser
from activity.models import Activity
from django.http import HttpRequest


# Create your views here.
def RestartActivityView(request, studentID, enrollmentID, activityID):
    try:
            if CustomUser.objects.filter(id=studentID).exists():
                student = CustomUser.objects.get(id=studentID)
                enrollment = Enrollment(id=enrollmentID)
                activity = Activity.objects.get(id=activityID)

                request = HttpRequest()
                request.method = 'POST'
                request.user = request.auth = None

                name = f'{student.email}_{enrollment.classroom.course.slug}_{enrollment.id}'
                projectID = activity.projectID

                data = {
                    "name": name,
                    "projectID": projectID
                }

                request.data = data



                try:
                    request_data = {
                        "name": name,
                    }

                    response = requests.post(
                        f"{settings.SIMULATION_SITE_DOMAIN}/v2/projects/{activity.base_activity.projectID}/duplicate",
                        auth=HTTPBasicAuth(settings.SIMULATION_AUTH_USERNAME, settings.SIMULATION_AUTH_PASSWORD),
                        json=request_data
                    )

                    if response.status_code == 201:
                        responseJSON = response.json()

                        newProjectID = responseJSON.data.get("project_id")

                        activity.projectID = newProjectID
                        activity.save()

                        return JsonResponse({"message":"successd"}, status=200)
                except Exception as e:
                     pass
            else:
                return JsonResponse({"error":"email not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": "Student not found"}, status=404)

def SaveActivityView(request , activityID):
    timeSpentInSeconds = request.POST.get("timeSpent")
    activity = Activity.objects.get(id=activityID)

    activity.time_spent = timeSpentInSeconds
    activity.save()

    return JsonResponse({"message":"successd"}, status=200)

def ScoresView(request, userID, activityID):
    course = None
    student_activity = None

    if CustomUser.objects.filter(id=userID).exists():
        student = CustomUser.objects.get(id=userID)
        activity = Activity(id=activityID)

        course = activity.course
    

    projectID = activity.projectID
    nodes = getAllNodes(projectID)
    allConfigs = getAllNodeConfigs(projectID, nodes)
    allConfigs["links"] = IntermediaryUtils.getAllLinks(projectID, nodes)

    correctConfigString = activity.base_activity.answer_key
    correctConfig = json.loads(correctConfigString)
    correctConfig = json.loads(correctConfig)

    points = activity1.getPoints(allConfigs, correctConfig)

    print(allConfigs)
    print('|')
    print('|')
    print('|')
    print(correctConfig)

    # return Response(allConfigs)
    return JsonResponse(points)

def SubmitActivityView(request):
    pass
