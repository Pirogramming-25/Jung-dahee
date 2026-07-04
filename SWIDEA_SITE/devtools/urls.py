from django.urls import path
from . import views

app_name = 'devtools'

urlpatterns = [
    path('', views.devtool_list, name='devtool_list'),
    path('create/', views.devtool_create, name='devtool_create'),
    path('<int:pk>/', views.devtool_detail, name='devtool_detail'),
    path('<int:pk>/update/', views.devtool_update, name='devtool_update'),
    path('<int:pk>/delete/', views.devtool_delete, name='devtool_delete'),
]
