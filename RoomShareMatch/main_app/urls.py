from django.urls import path
from . import views

app_name = 'main_app'

"""
path(route, view, kwargs, name)
第一引数(URL)にアクセスがあった時、第二引数の関数を呼び出し、第三引数にnameを設定する。
この name 属性は、テンプレート内でURLを参照するために使用されます。
"""
urlpatterns = [
    path('', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('user_home/', views.user_home, name='user_home'),
    path('user_home/auth_info/', views.auth_info, name='auth_info'),
    path('user_home/auth_info_saved/', views.update_auth_info, name='update_auth_info'),
    path('user_home/matching_profile/', views.matching_profile, name='matching_profile'),
    path('user_home/matching_profile_saved/', views.update_matching_profile, name='update_matching_profile'),
]

