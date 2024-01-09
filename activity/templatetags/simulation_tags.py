from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def gns3_project_url(activity):
    return f"{settings.SIMULATION_DOMAIN}static/web-ui/server/1/project/{activity}/"