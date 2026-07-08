from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/search/', views.post_search, name='post_search'),
    path('posts/create/', views.post_create, name='post_create'),
    path('posts/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('posts/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('posts/<int:pk>/comments/', views.comment_create, name='comment_create'),
    path('comments/<int:pk>/edit/', views.comment_edit, name='comment_edit'),
    path('comments/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
]
