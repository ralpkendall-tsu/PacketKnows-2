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
        print("Get the three classes you want to enroll the self-learner in")
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

        ITNactivities = []
        activities_to_saveITNTraining = createSelfLearnerActivity(instance, enrollmentITN, "training")
        activities_to_save += activities_to_saveITNTraining
        ITNactivities += activities_to_saveITNTraining
        activities_to_saveITNTesting = createSelfLearnerActivity(instance, enrollmentITN, "testing")
        activities_to_save += activities_to_saveITNTesting
        ITNactivities += activities_to_saveITNTesting
        try:
            Activity.objects.bulk_create(ITNactivities)
        except Exception as e:
            print(f"Error bulk creating ITN activities: {e}")
        enrollmentITN.activities.set(ITNactivities)

        SRWE_activities = []
        activities_to_saveSRWETraining = createSelfLearnerActivity(instance, enrollmentSRWE, "training")
        activities_to_save += activities_to_saveSRWETraining
        SRWE_activities += activities_to_saveSRWETraining
        activities_to_saveSRWETesting = createSelfLearnerActivity(instance, enrollmentSRWE, "testing")
        activities_to_save += activities_to_saveSRWETesting
        SRWE_activities += activities_to_saveSRWETesting
        Activity.objects.bulk_create(SRWE_activities)
        enrollmentSRWE.activities.set(SRWE_activities)

        # ENSA activities
        ENSA_activities = []
        activities_to_saveENSATraining = createSelfLearnerActivity(instance, enrollmentENSA, "training")
        activities_to_save += activities_to_saveENSATraining
        ENSA_activities += activities_to_saveENSATraining
        activities_to_saveENSATesting = createSelfLearnerActivity(instance, enrollmentENSA, "testing")
        activities_to_save += activities_to_saveENSATesting
        ENSA_activities += activities_to_saveENSATesting
        Activity.objects.bulk_create(ENSA_activities)
        enrollmentENSA.activities.set(ENSA_activities)

        

def createSelfLearnerActivity(instance, enrollment, mode):
    print("activity start")
    activities_to_save = []
    
    for activity in BaseActivity.objects.filter(course = enrollment.classroom.course):
        print(activity.number)
        baseProjectID = activity.projectID
        name = f"{instance.email}_{enrollment.classroom.course.slug}_{enrollment.id}_{mode}"
        print("name: " + name)
        
        try:
            request_data = {
                "name": name,
            }

            
            response = requests.post(
                f"{settings.SIMULATION_SITE_DOMAIN}v2/projects/{baseProjectID}/duplicate",
                auth=HTTPBasicAuth(settings.SIMULATION_AUTH_USERNAME, settings.SIMULATION_AUTH_PASSWORD),
                json=request_data
            )
            

            if response.status_code == 201:
                responseJSON = response.json()
                print(responseJSON)

                newProjectID = responseJSON.get("project_id")
                print(newProjectID)
                selfLearnerActivity = Activity(base_activity=activity, projectID=newProjectID, mode=mode)
                activities_to_save.append(selfLearnerActivity)
            else:
                print(response)
            
        except Exception as e:
            print(e)

    return activities_to_save