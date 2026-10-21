"""Vercel entrypoint using the same Python HTTP boundary as local development."""
from dionaea.http_api import APIHandler


class handler(APIHandler):
    pass
