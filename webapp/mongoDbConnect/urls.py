from django.urls import path

from . import views

urlpatterns = [
    path("", views.latest_data_table, name="latest_data_table"),
]