# -*- coding: utf-8 -*-
import random
import urllib.parse
from datetime import datetime

import requests

from .models import AlertEndpoint
from .models import AlertLog
from .models import ProfileChangelog


def _discord_notification(
    endpoint: AlertEndpoint, changelog: ProfileChangelog, message: str
) -> int:
    """Private function to send a message to a Discord wehhook

    Args:
        endpoint (AlertEndpoint): The alert endpoint (of service "discord")
        changelog (ProfileChangelog): The changelog to send the alert for.
        message (str): The message to send to the webhook.

    Returns:
        int: The status code returned from Discord.
    """
    timestamp = datetime.now()
    headers = {"content-type": "application/json"}
    payload = {
        "content": f"{message}",
        "nonce": random.randint(10000, 99999),
        "embed": {
            "title": "Theia Notification",
            "description": f'Sent at {timestamp.strftime("%Y-%m-%d %H:%M:%S")}',
        },
    }

    response = requests.post(endpoint.url, json=payload, headers=headers)
    AlertLog(
        server=changelog.server,
        alert_endpoint=endpoint.name,
        message=message,
        status_code=response.status_code,
    ).save()
    return response.status_code


def _msteams_notification(
    endpoint: AlertEndpoint, changelog: ProfileChangelog, message: str
) -> int:
    """Private function to send a message to a Microsoft Teams wehhook

    Args:
        endpoint (AlertEndpoint): The alert endpoint (of service "msteams")
        changelog (ProfileChangelog): The changelog to send the alert for.
        message (str): The message to send to the webhook.

    Returns:
        int: The status code returned from Microsoft.
    """
    headers = {"content-type": "application/json"}
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": endpoint.url,
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
                                            "text": changelog.server.name,
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
    response = requests.post(endpoint.url, json=payload, headers=headers)
    AlertLog(
        server=changelog.server,
        alert_endpoint=endpoint.name,
        message=message,
        status_code=response.status_code,
    ).save()
    return response.status_code


def _slack_notification(
    endpoint: AlertEndpoint, changelog: ProfileChangelog, message: str
) -> int:
    """Private function to send a message to a Slack wehhook

    Args:
        endpoint (AlertEndpoint): The alert endpoint (of service "slack")
        changelog (ProfileChangelog): The changelog to send the alert for.
        message (str): The message to send to the webhook.

    Returns:
        int: The status code returned from Slack.
    """
    headers = {"content-type": "application/json"}

    payload = {
        "text": message,
        "username": "Theia Notifications",
        "icon_emoji": ":bell:",
    }

    response = requests.post(endpoint.url, json=payload, headers=headers)

    AlertLog(
        server=changelog.server,
        alert_endpoint=endpoint.name,
        message=message,
        status_code=response.status_code,
    ).save()

    return response.status_code


def _telegram_notification(
    endpoint: AlertEndpoint, changelog: ProfileChangelog, message: str
) -> int:
    """Private function to send a message to a Telegram wehhook

    Args:
        endpoint (AlertEndpoint): The alert endpoint (of service "telegram")
        changelog (ProfileChangelog): The changelog to send the alert for.
        message (str): The message to send to the webhook.

    Returns:
        int: The status code returned from Telegram.
    """
    url_encoded_message = urllib.parse.quote(message)

    response = requests.get(endpoint.url + url_encoded_message)

    AlertLog(
        server=changelog.server,
        alert_endpoint=endpoint.name,
        message=message,
        status_code=response.status_code,
    ).save()

    return response.status_code


def send_alert(
    endpoint: AlertEndpoint, changelog: ProfileChangelog, message: str
) -> int:

    if endpoint.service == "discord":
        return _discord_notification(endpoint, changelog, message)
    elif endpoint.service == "msteams":
        return _msteams_notification(endpoint, changelog, message)
    elif endpoint.service == "slack":
        return _slack_notification(endpoint, changelog, message)
    elif endpoint.service == "telegram":
        return _telegram_notification(endpoint, changelog, message)
    else:
        raise RuntimeError(
            f"{endpoint}: {endpoint.service} is not a valid endpoint type!"
        )
