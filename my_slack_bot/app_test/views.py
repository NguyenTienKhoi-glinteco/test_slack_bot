from django.http import HttpResponse, JsonResponse
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import datetime

import json

client = WebClient(token="xoxb-6464755640310-6494295414032-t8iioiajXiONJngaRZ4js4fC")


def valid_date(date):
    return datetime.strptime(date, "%Y-%m-%d").date()


def get_data_form(payload):
    view = payload.get("view")
    state = view.get("state")
    state_value = state.get("values")

    form_data = {}
    for value in state_value.values():
        for key, value_ in value.items():
            form_data[key] = value_
    start_date_str = form_data["start_date_picker"]["selected_date"]
    end_date_str = form_data["end_date_picker"]["selected_date"]
    reason = form_data["plain_text_input-action"]["value"]

    start_date = valid_date(start_date_str)
    end_date = valid_date(end_date_str)

    return start_date, end_date, reason


@csrf_exempt
def event_hook(request):
    json_dict = json.loads(request.body.decode("utf-8"))
    if json_dict["token"] != settings.VERIFICATION_TOKEN:
        return HttpResponse(status=403)
    # return the challenge code here
    if "type" in json_dict:
        if json_dict["type"] == "url_verification":
            response_dict = {"challenge": json_dict["challenge"]}
            return JsonResponse(response_dict, safe=False)
    return HttpResponse(status=500)


def create_form():
    today = datetime.now().strftime("%Y-%m-%d")

    modal_payload = {
        "title": {"type": "plain_text", "text": "Glinteco vacation", "emoji": True},
        "submit": {"type": "plain_text", "text": "Send Request", "emoji": True},
        "type": "modal",
        "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Hi <fakelink.toUser.com|@User>!* Here's your request form:",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Start date:"},
                "accessory": {
                    "type": "datepicker",
                    "initial_date": today,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a date",
                        "emoji": True,
                    },
                    # "action_id": "start_date_picker",
                    "block_id": "start_date",
                },
            },
            {
                "block_id": "end_date",
                "type": "section",
                "text": {"type": "mrkdwn", "text": "End date:"},
                "accessory": {
                    "type": "datepicker",
                    "initial_date": today,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a date",
                        "emoji": True,
                    },
                    "action_id": "end_date_picker",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Section block with radio buttons"},
                "accessory": {
                    "type": "radio_buttons",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Half day afternoon",
                                "emoji": True,
                            },
                            "value": "value-0",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Half day afternoon",
                                "emoji": True,
                            },
                            "value": "value-1",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Full day",
                                "emoji": True,
                            },
                            "value": "value-2",
                        },
                    ],
                    "action_id": "radio_buttons-action",
                },
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "plain_text_input-action",
                },
                "label": {"type": "plain_text", "text": "Reason", "emoji": True},
            },
        ],
    }
    return modal_payload


def create_message_block(start_date, end_date, reason, user_name):
    message_block = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*You have a new request from <@%s>*" % user_name,
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Start date:*" + f" {start_date}"},
                {"type": "mrkdwn", "text": "*End date:*" + f" {end_date}"},
                {"type": "mrkdwn", "text": "*Reason:*" + f" {reason}"},
            ],
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Approve"},
                    "style": "primary",
                    "value": "click_me_123",
                    "action_id": "approve",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Deny"},
                    "style": "danger",
                    "value": "click_me_123",
                    "action_id": "denied",
                },
            ],
        },
    ]

    message_ok = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Your vacation request has successfully been sent!* \n*Admin* will review your request soon.",
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Start Date:*" + f" {start_date}"},
                {"type": "mrkdwn", "text": "*Requested at:*" + f" {datetime.now()}"},
                {"type": "mrkdwn", "text": "*End date:*" + f" {end_date}"},
                {"type": "mrkdwn", "text": "*Note:* " + f" {reason}"},
            ],
        },
        {"type": "divider"},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "New request",
                    },
                    "style": "primary",
                    "value": "click_me_123",
                    "action_id": "approved",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Cancle request"},
                    "style": "danger",
                    "value": "click_me_123",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Main menu", "emoji": True},
                    "value": "click_me_123",
                    "action_id": "denied",
                },
            ],
        },
    ]

    return message_block, message_ok


@csrf_exempt
def slack_command(request):
    
    trigger_id = request.POST.get("trigger_id")

    try:
        client.views_open(trigger_id=trigger_id, view=create_form())
    except SlackApiError as e:
        print(f"Error opening modal: {e}")
    return HttpResponse()


@csrf_exempt
def slack_submission(request):
    error_object = {
        "response_action": "errors",
        "errors": {"start_date": "The end date must be greater than the start date"}
    }
    print(error_object)
    return JsonResponse(error_object)

    payload = json.loads(request.POST.get("payload"))
    
    user_name = payload.get("user", {}).get("name")

    

    current_date = datetime.now().date()

    user_id = payload.get("user", {}).get("id")

    

    if payload.get("type") == "view_submission":
        start_date, end_date, reason = get_data_form(payload)
        message_block, message_ok = create_message_block(start_date, end_date, reason, user_name)

        if start_date > end_date:
            error_object = {
                "response_action": "errors",
                "errors": {"end_date": "The end date must be greater than the start date"}
            }
            print(error_object)
            return JsonResponse(error_object)
        else:
            try:
                admin_ids = []

                for user in client.users_list()["members"]:
                    if user.get("is_admin", False) or "admin" in user.get("roles", []):
                        admin_ids.append(user["id"])
                for admin_id in admin_ids:
                    client.chat_postMessage(
                        channel=admin_id, blocks=message_block, text="success"
                    )

                client.chat_postMessage(
                    channel=user_id, blocks=message_ok, text="sucess"
                )
                return HttpResponse()
            except SlackApiError as e:
                return JsonResponse(e)
    
    if payload.get("type") == "block_actions":
        
        action_id = payload["actions"][0]["action_id"]
        chanel_id = payload.get("channel", {}).get("id")
        
        if action_id == "approve":
            time_stamp = payload.get('message')['ts']

            
            client.chat_update(channel= chanel_id, ts = time_stamp, text="", blocks=[
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*You have a new request from <@%s>*" % user_name,
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Start date:*"},
                {"type": "mrkdwn", "text": "*End date:*"},
                {"type": "mrkdwn", "text": "*Reason:*" },
            ],
        }
    ])

            return HttpResponse()

    return HttpResponse()


# def approve_deny(request):
#      payload = json.loads(request.POST.get('payload'))
#      breakpoint()
#      if payload.get("type") == "block_actions":
#         user_id = payload.get("user", {}).get("id")
#         client.chat_postMessage(channel= user_id, text='approved')
#         return HttpResponse()
