from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('change_password/', views.change_password, name="change_password"),
    path('update_profile/', views.update_profile, name="update_profile"),
]