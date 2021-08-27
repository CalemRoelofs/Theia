# -*- coding: utf-8 -*-
import re

from django.core.exceptions import ValidationError

DISCORD_VALIDATOR = re.compile(
    r"https:\/\/discord.com\/api\/webhooks\/([^\/]+)\/([^\/]+)"
)
TELEGRAM_VALIDATOR = re.compile(
    r"https:\/\/api.telegram.org\/bot[^\/]+\/sendMessage\?chat_id=-?[\d]+&text="
)
SLACK_VALIDATOR = re.compile(
    r"https:\/\/hooks.slack.com\/services\/[^\/]+\/[^\/]+\/[^\/]+"
)
MSTEAMS_VALIDATOR = re.compile(
    r"https:\/\/[^\/]+.webhook.office.com\/webhookb2\/[^\/]+\/IncomingWebhook\/[^\/]+\/[^\/]+"
)


def webhook_validator(url: str) -> bool:
    if "discord" in url:
        valid = bool(re.match(DISCORD_VALIDATOR, url))
        service = "Discord"

    elif "telegram" in url:
        valid = bool(re.match(TELEGRAM_VALIDATOR, url))
        service = "Telegram"
    elif "slack" in url:
        valid = bool(re.match(SLACK_VALIDATOR, url))
        service = "Slack"
    elif "office.com" in url:
        valid = bool(re.match(MSTEAMS_VALIDATOR, url))
        service = "MS Teams"
    else:
        valid = False
        service = None

    if not service:
        message = "We can't figure out what webhook service you're trying to set up, but it's not supported."
    else:
        message = f"Something's not right with that url for {service}, please check it and try again."

    if not valid:
        raise ValidationError(message)

    return valid
