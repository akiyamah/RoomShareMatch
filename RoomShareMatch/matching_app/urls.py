from django.urls import path
from . import views

app_name = 'matching_app'

urlpatterns = [
    path('roommate_preference_view/', views.roommate_preference_view, name='roommate_preference_view'),
    path('roommate_preference_save/', views.save_roommate_preference, name='save_roommate_preference'),
    path('matching/new/', views.match_new, name='match_new'),
    path('matching/recommend/', views.match_recommend, name='match_recommend'),
    path('matching/search/', views.match_search, name='match_search'),
    path('matching/user_detail/<int:user_id>/', views.user_detail, name='user_detail'),
]
