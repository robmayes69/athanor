from django.conf.urls import include, url
from evennia.web import urls as evennia_urls
from athanor.rest.view import router as who_router

urlpatterns = [
    url(r'^', include(evennia_urls.urlpatterns)),
    url(r'^', include(who_router().urls))
]