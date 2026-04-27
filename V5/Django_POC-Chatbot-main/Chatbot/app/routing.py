from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path("ws/extension/WS/", consumers.Web_Search_Extension.as_asgi()),
    re_path("ws/extension/IT/", consumers.IT_Extension.as_asgi()),
    re_path("ws/extension/BNS/", consumers.BNS_Extension.as_asgi()),
    re_path("ws/extension/BSA/", consumers.BSA_Extension.as_asgi()),
    re_path("ws/extension/DPDP/", consumers.DPDP_Extension.as_asgi()),
    re_path("ws/extension/All/", consumers.Chat_Extension.as_asgi()),
]
