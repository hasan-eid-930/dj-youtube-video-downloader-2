from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    # path(
    #     "ws/adaptive-download/<str:room_name>/<str:video_id>/",
    #     consumers.ProgressBarConsumer.as_asgi(),
    # ),
    re_path(
        r"ws/(?P<room_name>\w+)/$",
        consumers.AdaptiveDownloadConsumer.as_asgi(),
        name='ws-adaptive-download'
    ),
]