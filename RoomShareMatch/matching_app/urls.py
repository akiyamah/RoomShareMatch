from django.urls import path
from . import views

app_name = 'matching_app'

urlpatterns = [
    path('roommate_preference/', views.roommate_preference, name='roommate_preference'),
    path('roommate_preference_save/', views.roommate_preference_save, name='roommate_preference_save'),
    path('roommate_preference/saved', views.roommate_preference_saved, name='roommate_preference_saved'),
    path('matching/new/', views.match_new, name='match_new'),
    path('matching/recommend/', views.match_recommend, name='match_recommend'),
    path('matching/search/', views.match_search, name='match_search'),
    path('user_detail/<int:user_id>/', views.get_show_user_detail, name='user_detail'),
]
