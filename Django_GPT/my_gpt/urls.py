from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sentiment/", views.sentiment_page, name="sentiment_page"),
    path("sentiment/run/", views.sentiment_run, name="sentiment_run"),
    path("summarize/", views.summarize_page, name="summarize_page"),
    path("summarize/run/", views.summarize_run, name="summarize_run"),
    path("moderate/", views.moderate_page, name="moderate_page"),
    path("moderate/run/", views.moderate_run, name="moderate_run"),
]
