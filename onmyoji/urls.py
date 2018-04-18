from django.conf.urls import url
from . import views

app_name = 'onmyoji'

urlpatterns = [
    url(r'^$', views.wanted, name='wanted'),
    url(r'^find', views.find, name='find'),
    url(r'^all', views.all, name='all'),
]
