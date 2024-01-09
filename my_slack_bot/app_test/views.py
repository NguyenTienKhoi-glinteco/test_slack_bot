from django.http import HttpResponse, JsonResponse
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from django.views.decorators.csrf import csrf_exempt
import json


client = WebClient(token="xoxb-6372324218561-6435060597218-tn7RYHPTxdsA3xrC04tyPv5d")

@csrf_exempt
def handle_slack_event(request):
    if request.method == "POST":
        
        payload = json.loads(request.body.decode('utf-8'))
        event = payload.get("type")
        breakpoint()
        if event == "url_verification":
            return HttpResponse(payload.get("challenge"))
        if event == "view_submission":
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

    command = request.POST.get('command')
    
    if command == "/glint-bot":
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


# @csrf_exempt
# def handle_submit_form(request):
#     payload = json.load(request.body)
#     if payload:
#         form_type = payload.get('type')
#         form_view = payload.get('view')
#         user_id = payload.get('user')
#         if form_type == 'view_submission':
#             values = form_view['state']['values']
#             option_1_value = values['block_option_1']['option_1']['value']
#             option_2_value = values['block_option_2']['option_2']['value']

#             response = client.chat_postMessage(channel=user_id,text = "success")
#         else:
#             return JsonResponse({"error": "Invalid command"}, status=400)


