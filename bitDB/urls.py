from django.urls import path
from django.conf.urls import url

from bitDB import views

urlpatterns = [
    url(r'^index/$', views.get_name),
]
