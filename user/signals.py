from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
import requests
from requests.auth import HTTPBasicAuth
from user.models import CustomUser
from classroom.models import Classroom, Enrollment
from activity.models import Activity, BaseActivity

@receiver(post_save, sender=CustomUser)
def auto_enroll_self_learner(sender, instance, created, **kwargs):
    if created and instance.category.name == "Self Learner":
        print("Signal for Self Learner working!")
        # Get the three classes you want to enroll the self-learner in
        classITN = Classroom.objects.get(code="ITN", instructor__isnull=True)
        classSRWE = Classroom.objects.get(code="SRWE", instructor__isnull=True)
        classENSA = Classroom.objects.get(code="ENSA", instructor__isnull=True)

        # Create Enrollment instances for each class
        enrollmentITN = Enrollment(student=instance, classroom=classITN)
        enrollmentSRWE = Enrollment(student=instance, classroom=classSRWE)
        enrollmentENSA = Enrollment(student=instance, classroom=classENSA)

        # Save the Enrollment instances
        enrollmentITN.save()
        enrollmentSRWE.save()
        enrollmentENSA.save()

        # Create Activity instances for each class
        activities_to_save = []

        activities_to_save += createSelfLearnerActivity(instance, enrollmentITN, "training")
        activities_to_save += createSelfLearnerActivity(instance, enrollmentITN, "testing")
        activities_to_save += createSelfLearnerActivity(instance, enrollmentSRWE, "training")
        activities_to_save += createSelfLearnerActivity(instance, enrollmentSRWE, "testing")
        activities_to_save += createSelfLearnerActivity(instance, enrollmentENSA, "training")
        activities_to_save += createSelfLearnerActivity(instance, enrollmentITN, "testing")

        Activity.objects.bulk_create(activities_to_save)
        

def createSelfLearnerActivity(instance, enrollment, mode):
    activities_to_save = []
    
    for activity in BaseActivity.objects.filter(course = enrollment.classroom.course):
        baseProjectID = activity.projectID
        name = f"{instance.email}_{enrollment.classroom.course.slug}_{enrollment.id}"
        
        try:
            request_data = {
                "name": name,
            }

            response = requests.post(
                f"{settings.SIMULATION_SITE_DOMAIN}/v2/projects/{baseProjectID}/duplicate",
                auth=HTTPBasicAuth(settings.SIMULATION_AUTH_USERNAME, settings.SIMULATION_AUTH_PASSWORD),
                json=request_data
            )

            if response.status_code == 201:
                responseJSON = response.json()

                newProjectID = responseJSON.data.get("project_id")
                selfLearnerActivity = Activity(base_activity=activity, projectID=newProjectID, mode=mode)
                activities_to_save.append(selfLearnerActivity)
        except Exception as e:
            pass

    return activities_to_save