from django.urls import path

from . import views

app_name = 'stories'

urlpatterns = [
    path('create/', views.story_create, name='story_create'),
    path('<int:pk>/', views.story_view, name='story_view'),
    path('<int:pk>/delete/', views.story_delete, name='story_delete'),
]
