'''
DjangoのSignal（シグナル）とは、アプリケーションの実行中に起こるイベントで、特定の処理をおこなえる機能です。
'''

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, UserPurpose, UserDesiredCohabitee, UserRoomLayout, UserRent
from matching_app.models import RoommatePreference

@receiver(post_save, sender=User)
def create_related_objects(sender, instance, created, **kwargs):
    # Userモデル作成(ユーザー登録)後にこの関数は自動で実行されUser.userに関連するオブジェクトを作成する。
    print('create_related_objects 起動')
    if created:
        # main_app.modelsに定義したuser関連obj
        UserProfile.objects.create(user=instance)
        UserPurpose.objects.create(user=instance)
        UserDesiredCohabitee.objects.create(user=instance)
        UserRoomLayout.objects.create(user=instance)
        UserRent.objects.create(user=instance)
        
        
        # matching_app.modelsに定義したuser関連obj
        RoommatePreference.objects.create(user=instance)
        
