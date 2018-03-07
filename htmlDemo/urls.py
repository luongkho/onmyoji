from django.conf.urls import url
from . import views

app_name = 'htmlDemo'

urlpatterns = [
    url(r'^$', views.wanted, name='wanted'),
]
