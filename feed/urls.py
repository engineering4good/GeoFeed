from django.conf.urls import url

from . import views

app_name = 'feed'
urlpatterns = [
    url(r'^$', views.vue_app, name='index'),
    url(r'^app/$', views.vue_app, name='vue_app'),
    url(r'^post/$', views.post, name='post'),
    url(r'^f/(?P<feed_secret>.+?)/', views.feed, name='feed'),
    url(r'^l/(?P<latitude>[^,]+?),(?P<longitude>[^,]+?)/', views.feed_public, name='feed.public'),
]
