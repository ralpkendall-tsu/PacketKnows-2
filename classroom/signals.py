from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from activity.models import Activity, BaseActivity
from classroom.models import Enrollment
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings

@receiver(post_save, sender=Enrollment)
def create_activities(sender, instance, created, **kwargs):
    if created and instance.student.category.name == "Student":
        try:
            activities_to_save = []
            created_activities_training = create_enrollment_activities(instance, "training")
            activities_to_save += created_activities_training
            created_activities_testing = create_enrollment_activities(instance, "testing")
            activities_to_save += created_activities_testing

            # Save the created activities
            Activity.objects.bulk_create(activities_to_save)
            print("Activities created!!")
            # Set the created activities to the Enrollment instance
            instance.activities.set(activities_to_save)
            print("Activities set to enrollment!!")
        except Exception as e:
            print(e)

def create_enrollment_activities(enrollment, mode):
    activities_to_save = []

    for activity in BaseActivity.objects.filter(course=enrollment.classroom.course):
        base_project_id = activity.projectID
        name = f"{enrollment.student.email}_{enrollment.classroom.course.slug}_{enrollment.id}_{mode}"

        try:
            request_data = {"name": name}

            # You need to adjust the API endpoint and authentication based on your specific implementation
            response = requests.post(
                f"{settings.SIMULATION_SITE_DOMAIN}v2/projects/{base_project_id}/duplicate",
                auth=HTTPBasicAuth(settings.SIMULATION_AUTH_USERNAME, settings.SIMULATION_AUTH_PASSWORD),
                json=request_data,
            )

            if response.status_code == 201:
                response_json = response.json()
                new_project_id = response_json.get("project_id")

                enrollment_activity = Activity(base_activity=activity, projectID=new_project_id, mode=mode)
                activities_to_save.append(enrollment_activity)
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Exception during activity creation: {e}")


    return activities_to_save  # Return the created activities