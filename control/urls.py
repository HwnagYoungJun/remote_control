from django.urls import path
from . import views

urlpatterns = [
    path("start/", views.StartView.as_view(), name='start'),
    path("end/", views.EndView.as_view(), name='end'),
]