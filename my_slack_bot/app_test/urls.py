from django.urls import path
from .views import handle_slack_event, slack_command

urlpatterns = [
    path('events/', handle_slack_event, name = 'slack_event'),
    path('commands/', slack_command, name = 'slack_command'),
    #path('send/', handle_submit_form, name="send_request"),
]