from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.PirostagramLoginView.as_view(), name='login'),
    path('logout/', views.PirostagramLogoutView.as_view(), name='logout'),
    path('search/', views.user_search, name='user_search'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
]
