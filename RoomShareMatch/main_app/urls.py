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
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('user_home/', views.user_home, name='user_home'),
    path('logout/', views.logout, name='logout'),
    path('user_home/auth_info_edit/', views.auth_info_edit, name='auth_info_edit'),
    path('user_home/matching_profile/', views.matching_profile_edit, name='matching_profile_edit'),
]

