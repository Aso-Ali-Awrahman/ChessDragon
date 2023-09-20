from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name="home"),
    path('community/', views.community_page, name='community'),
    path('login/', views.login_page, name='login'),
    
    path('profile/', views.profile_page, name='profile'),
    path('super-profile/', views.super_profile_page, name='super-profile'),
   
    path('standing/', views.standing_page, name='standing'),
    path('tournament/', views.tournament_page, name='tournament'),
    path('round-play/', views.round_page, name='round-play'),
    path('knock-out/', views.knockout_page, name='knock-out'),
    
    path('<str:message>/', views.error_page, name='error-page'),
]