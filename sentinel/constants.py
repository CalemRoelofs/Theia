# -*- coding: utf-8 -*-
SECURITY_HEADERS_WHITELIST = {
    "Cache-Control",
    "Content-Security-Policy",
    "Content-Type",
    "Cross-Origin-Embedder-Policy",
    "Cross-Origin-Opener-Policy",
    "Cross-Origin-Resource-Policy",
    "Expect-CT",
    "Permissions-Policy",
    "Pragma",
    "Referrer-Policy",
    "Server",
    "Strict-Transport-Security",
    "Vary",
    "X-Content-Type-Options",
    "X-Frame-Options",
}

SCAN_FREQUENCY_CHOICES = (
    ("minutes", "Minutes"),
    ("hours", "Hours"),
    ("days", "Days"),
    ("weeks", "Weeks"),
)

ENDPOINT_TYPE_CHOICES = (
    ("discord", "Discord"),
    ("msteams", "Microsoft Teams"),
    ("slack", "Slack"),
    ("telegram", "Telegram"),
    ("email", "Email"),
)
