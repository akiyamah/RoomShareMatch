# Generated by Django 4.1.7 on 2023-03-20 14:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RoommatePreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('male', '男性'), ('female', '女性'), ('other', 'その他')], max_length=10)),
                ('age_min', models.IntegerField(default=18)),
                ('age_max', models.IntegerField(default=30)),
                ('occupation', models.CharField(blank=True, max_length=255)),
                ('lifestyle', models.CharField(blank=True, max_length=255)),
                ('purpose', models.CharField(blank=True, max_length=255)),
                ('rent', models.IntegerField(default=0)),
                ('duration', models.CharField(choices=[('short', '短期(1〜3ヶ月)'), ('mid', '中期(3ヶ月〜1年)'), ('long', '長期(1年以上)')], max_length=10)),
                ('smoking', models.BooleanField(default=False)),
                ('layout', models.CharField(blank=True, max_length=255)),
                ('location', models.CharField(blank=True, max_length=255)),
                ('room_size', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]