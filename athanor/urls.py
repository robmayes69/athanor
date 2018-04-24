from django.conf.urls import include, url
from evennia.web import urls as evennia_urls

urlpatterns = [
    url(r'^', include(evennia_urls.urlpatterns)),
]