from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$',  views.about, name='about'),
    url(r'^new/$', views.new_room, name='new_room'),
    url(r'^accounts/login/', views.login, name='account_login'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),  # admin site
    url(r'^(?P<label>[\w-]{,50})/$', views.chat_room, name='chat_room'),
    url(r'^(?P<label>[\w-]{,50})/leave/$', views.leave_chat, name='leave_room'),


]