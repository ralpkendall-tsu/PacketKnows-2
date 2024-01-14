from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Activity
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.http import JsonResponse

@receiver(post_delete, sender=Activity)
def activity_deleted(sender, instance, **kwargs):
    try:
        # remove on GNS3
        response = requests.delete(settings.SIMULATION_SITE_DOMAIN + "/v2/projects/" + instance.projectID,
        auth=HTTPBasicAuth(settings.SIMULATION_AUTH_USERNAME, settings.SIMULATION_AUTH_PASSWORD))
    
        return JsonResponse({'message': 'Successfully deleted'}, status=200)
    except requests.RequestException as e:
        # Handle request exceptions (e.g., connection error)
        return JsonResponse({'error': f'API request error: {str(e)}'}, status=500)