'''
Djangoにはプロジェクトの作成と同時に自動でデータの管理画面が作成されます。
この管理画面で表示するデータの設定や機能の追加などをここで行います。
ここは管理者画面の立ち位置なので、会員登録機能などで作られるユーザーでは入ることができず、
スタッフ権限を持ったユーザーのみがログインして閲覧することができます。
'''

from django.contrib import admin
from .models import UserProfile

# Register your models here.

admin.site.register(UserProfile)
