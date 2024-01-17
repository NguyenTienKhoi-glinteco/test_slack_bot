from django.urls import path
from .views import slack_command, slack_submission

urlpatterns = [
    #path('events/', handle_slack_event, name = 'slack_event'),
    path('commands/', slack_command, name = 'slack_command'),
    path('send/', slack_submission, name="send_request"),
    # path('eventhook/', event_hook, name="send_request"),
    #path('approve/', approve_deny, name="approve_deny"),
]