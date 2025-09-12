# from django.urls import re_path
# from . import consumers

# websocket_urlpatterns = [
#     re_path(r'^ws/support/(?P<session_id>\d+)/(?P<token>[0-9a-f-]+)/$', consumers.SupportConsumer.as_asgi()),
# ]





# from django.urls import re_path
# from . import consumers

# websocket_urlpatterns = [
#     re_path(r'ws/support/(?P<session_id>\w+)/$', consumers.SecureSupportConsumer.as_asgi()),
# ]



from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/support/(?P<session_id>[\w-]+)/$', consumers.SecureSupportConsumer.as_asgi()),
]
