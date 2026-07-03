from django.urls import path
from . import views

urlpatterns = [
    path('', views.idea_list, name='idea_list'),
    path('search/', views.idea_search_ajax, name='idea_search_ajax'),
    path('create/', views.idea_create, name='idea_create'),
    path('<int:pk>/', views.idea_detail, name='idea_detail'),
    path('<int:pk>/update/', views.idea_update, name='idea_update'),
    path('<int:pk>/delete/', views.idea_delete, name='idea_delete'),
    path('<int:pk>/star/', views.idea_star_toggle, name='idea_star_toggle'),
    path('<int:pk>/interest/', views.idea_interest_change, name='idea_interest_change'),
]
