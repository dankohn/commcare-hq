from django.conf.urls import url
from corehq.messaging.smsbackends.infobip.views import InfobipIncomingMessageView


urlpatterns = [
    url(r'^message/(?P<api_key>[\w-]+)/?$$', InfobipIncomingMessageView.as_view(),
        name=InfobipIncomingMessageView.urlname)
]
