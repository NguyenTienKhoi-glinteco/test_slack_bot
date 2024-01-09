from django.http import HttpResponse, JsonResponse
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json

client = WebClient(token="xoxb-6372324218561-6435060597218-KiTUCrGK73qiM6BZNN3svSJ2")

@csrf_exempt
def event_hook(request):
    json_dict = json.loads(request.body.decode('utf-8'))
    if json_dict['token'] != settings.VERIFICATION_TOKEN:
        return HttpResponse(status=403)
    #return the challenge code here
    if 'type' in json_dict:
        if json_dict['type'] == 'url_verification':
            response_dict = {"challenge": json_dict['challenge']}
            return JsonResponse(response_dict, safe=False)
    return HttpResponse(status=500)


@csrf_exempt
def handle_slack_event(request):
    if request.method == "POST":
        
        payload = json.loads(request.body.decode('utf-8'))
        event = payload.get("type")
        if event == "url_verification":
            return HttpResponse(payload.get("challenge"))

        if event == "event_callback":
            data = payload.get("event")
            try:
                client.chat_postMessage(
                    channel = data.get("channel"),
                    text="Hello from your Django app!"
                )
            except SlackApiError as e:
                print(f"Error: {e}")
        return HttpResponse("")


@csrf_exempt
def slack_command(request):
    
    trigger_id = request.POST.get('trigger_id')
    modal_payload = {
        "title": {
            "type": "plain_text",
            "text": "Request Leave"
        },
        "submit": {
            "type": "plain_text",
            "text": "Send Request"
        },
        "blocks": [
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "option_1",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "First option"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Option 1"
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "option_2",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "How many options do they need, really?"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Option 2"
                }
            },
        ],                      
        "type": "modal"
    }
    response = client.views_open(trigger_id=trigger_id, view=modal_payload)
    return HttpResponse()
    if response['ok']:
        return HttpResponse()
    command = request.POST.get('command')
    
    if command == "/hello":
        try:
            trigger_id = request.POST.get('trigger_id')
            modal_payload = {
                "title": {
                    "type": "plain_text",
                    "text": "Request Leave"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Send Request"
                },
                "blocks": [
                    {
                        "type": "input",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "option_1",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "First option"
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Option 1"
                        }
                    },
                    {
                        "type": "input",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "option_2",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "How many options do they need, really?"
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Option 2"
                        }
                    },
                ],                      
                "type": "modal"
            }
            
            response = client.views_open(trigger_id=trigger_id, view=modal_payload)
            if response['ok']:
                return HttpResponse()
            else:
                return JsonResponse({"error": f"Failed to open modal. Error: {response['error']}"}, status=500)
        except SlackApiError as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid command"}, status=400)


@csrf_exempt
def slack_submission(request):
    payload = json.loads(request.POST.get('payload'))
    if payload.get("type") == "view_submission":
        user_id = payload.get("user", {}).get("id")
        client.chat_postMessage(channel= user_id, text='OK')

        admin_ids = []
        message_block = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "You have a new request:\n*<fakeLink.toEmployeeProfile.com|Fred Enriquez - New device request>*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Type:*\nComputer (laptop)"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*When:*\nSubmitted Aut 10"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Last Update:*\nMar 10, 2015 (3 years, 5 months)"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Reason:*\nAll vowel keys aren't working."
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Specs:*\n\"Cheetah Pro 15\" - Fast, really fast\""
                        }
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Approve"
                            },
                            "style": "primary",
                            "value": "click_me_123",
                            "action_id": "approve",
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Deny"
                            },
                            "style": "danger",
                            "value": "click_me_123"
                        }
                    ]
                }
            ]
        for user in client.users_list()["members"]:
            if user.get('is_admin', False) or "admin" in user.get("roles", []):
                admin_ids.append(user["id"])
        for admin_id in admin_ids:
            client.chat_postMessage(channel=admin_id, text="This is message for admin", blocks=message_block)
        
        return HttpResponse()
    if payload.get("type") == "block_actions":
        user_id = payload.get("user", {}).get("id")
        client.chat_postMessage(channel= user_id, text='approved')
        return HttpResponse()


# def approve_deny(request):
#      payload = json.loads(request.POST.get('payload'))
#      breakpoint()
#      if payload.get("type") == "block_actions":
#         user_id = payload.get("user", {}).get("id")
#         client.chat_postMessage(channel= user_id, text='approved')
#         return HttpResponse()
