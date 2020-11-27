from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from . import consumers
from django.conf.urls import url

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            url(r"^xoxcomputer/$",consumers.ComputerConsumer),
            url(r"^xoxfriend/$",consumers.FriendConsumer),
        ])
    ),
})