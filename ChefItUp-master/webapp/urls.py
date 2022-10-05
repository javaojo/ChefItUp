from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.home_view, name='home_view'),
]
