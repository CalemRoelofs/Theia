# -*- coding: utf-8 -*-
import random
from datetime import datetime

import requests

from .models import AlertEndpoint
from .models import AlertLog
from .models import ProfileChangelog


def discord_notification(endpoint: AlertEndpoint, changelog: ProfileChangelog) -> int:
    """Function so send an alert via Discord to a configured Webhook.

    Args:
        endpoint (AlertEndpoint): The endpoint object to get the details from.
        changelog (ProfileChangelog): The chnage to send the alert about.

    Returns:
        int: The status code returned from Discord.
    """
    timestamp = datetime.now()
    message = f"""
    Alert:
    \tServer:       {changelog.server_profile.server.name}
    \tService:      {changelog.changed_field}
    \tOld Value:    {changelog.old_value}
    \tNew Value:    {changelog.new_value}
    """
    headers = {"content-type": "application/json"}
    payload = {
        "content": f"{message}",
        "nonce": random.randint(10000, 99999),
        "embed": {
            "title": "LiveWire Notification",
            "description": f'Sent at {timestamp.strftime("%Y-%m-%d %H:%M:%S")}',
        },
    }

    response = requests.post(endpoint.endpoint_value, json=payload, headers=headers)
    AlertLog(
        timestamp=timestamp,
        server=changelog.server_profile.server,
        alert_endpoint=endpoint,
        message=message,
        status_code=response.status_code,
    ).save()
    return response.status_code


def msteams_notification(endpoint: AlertEndpoint, changelog: ProfileChangelog) -> int:
    timestamp = datetime.now()
    message = f"""
    # Alert: Change Detected!\n
    \tServer:       {changelog.server_profile.server.name}\n
    \tService:      {changelog.changed_field}\n
    \tOld Value:    {changelog.old_value}\n
    \tNew Value:    {changelog.new_value}\n
    """
    headers = {"content-type": "application/json"}
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": endpoint.endpoint_value,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {"type": "TextBlock", "text": "Alert from Theia", "wrap": True},
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": 2,
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "Server:",
                                            "wrap": True,
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": "Service:",
                                            "wrap": True,
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": "Old Value",
                                            "wrap": True,
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": "New Value",
                                            "wrap": True,
                                        },
                                    ],
                                },
                                {
                                    "type": "Column",
                                    "width": 2,
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": changelog.server_profile.server.name,
                                            "wrap": True,
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": changelog.changed_field,
                                            "wrap": True,
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": changelog.old_value,
                                            "wrap": True,
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": changelog.new_value,
                                            "wrap": True,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            }
        ],
    }
    response = requests.post(endpoint.endpoint_value, json=payload, headers=headers)
    AlertLog(
        timestamp=timestamp,
        server=changelog.server_profile.server,
        alert_endpoint=endpoint,
        message=message,
        status_code=response.status_code,
    ).save()
    return response.status_code
