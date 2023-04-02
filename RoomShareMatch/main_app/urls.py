from django.urls import path
from . import views

app_name = 'main_app'

"""
path(route, view, kwargs, name)
第一引数(URL)にアクセスがあった時、第二引数の関数を呼び出し、第三引数にnameを設定する。
この name 属性は、テンプレート内でURLを参照するために使用されます。
"""
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('user_home_view/', views.user_home_view, name='user_home_view'),
    path('user_home/auth_info_view/', views.update_auth_info, name='update_auth_info'),
    path('user_home/matching_profile_view/', views.matching_profile_view, name='matching_profile_view'),
    path('user_home/matching_profile_saved/', views.update_matching_profile, name='update_matching_profile'),
]

