'''
前章のMTVフレームワークで触れたM（モデル）の部分であり、DBに登録するテーブルを記述していきます。
基本的にはClassベースで記述していき、最終的にmigrateというアクションでデータ構造をデータベースに登録します。
'''

from django.db import models
from django.contrib.auth.models import User


# ルームシェア希望条件を表すモデルクラス(単一な回答の場合フィールドのみまとめたモデル)
class RoommatePreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roommate_preference')
    gender = models.CharField(max_length=6, verbose_name='性別')
    age_min = models.IntegerField(blank=True, null=True, verbose_name='最小年齢')
    age_max = models.IntegerField(blank=True, null=True, verbose_name='最大年齢')
    occupation = models.CharField(max_length=10, verbose_name='職業')
    period = models.CharField(max_length=10, verbose_name='期間')
    smoking = models.CharField(max_length=10, verbose_name='喫煙')
    pet = models.CharField(max_length=10, verbose_name='ペット')
    prefecture = models.CharField(max_length=10, verbose_name='都道府県')
    commute_time = models.CharField(max_length=10, verbose_name='通勤時間')
    parking = models.CharField(max_length=10, verbose_name='駐車場')

# 目的
class Purpose(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purposes')
    purpose_name = models.CharField(max_length=200, verbose_name='目的名')
    

# 同居人数
class DesiredCohabitee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='desired_cohabitees')
    cohabitation_number = models.CharField(max_length=30, verbose_name='同居人数')
    

# 部屋の間取り
class RoomLayout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_layout')
    layout = models.CharField(max_length=50, verbose_name='間取り')
    

# 家賃
class Rent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rent')
    rent = models.CharField(max_length=100, verbose_name='家賃')
    
    
    def show_gender(self):
        return self.gender
    
    def get_age_range(self):
        return f"{self.age_min}歳〜{self.age_max}歳"
