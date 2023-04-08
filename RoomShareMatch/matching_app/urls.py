from django.urls import path
from . import views

app_name = 'matching_app'

urlpatterns = [
    path('roommate_preference/', views.roommate_preference, name='roommate_preference'),
    path('update_roommate_preference/', views.update_roommate_preference, name='update_roommate_preference'),
    path('matching/new_users/', views.match_new_users, name='match_new_users'),
    path('matching/recommend_users/', views.match_recommend_users, name='match_recommend_users'),
    path('matching/search_users/', views.match_search_users, name='match_search_users'),
    path('matching/user_detail/<int:user_id>/', views.user_detail, name='user_detail'),
]
