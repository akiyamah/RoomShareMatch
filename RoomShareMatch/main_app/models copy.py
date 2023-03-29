from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    """
    UserProfileモデルは、ユーザーのプロフィール情報を管理します。
    それぞれのユーザーは、自分のプロフィール情報を通じて他のユーザーとマッチングや交流を行います。

    Attributes:
        user (OneToOneField): Userモデルと1対1の関係を持ちます。
        user_email (EmailField): ユーザーのメールアドレス。
        user_first_name (CharField): ユーザーの名前。
        user_last_name (CharField): ユーザーの姓。
        sex (CharField): ユーザーの性別。
        day_of_birth (DateField): ユーザーの誕生日。
        age (IntegerField): ユーザーの年齢。
        profession (CharField): ユーザーの職業。
        self_introduction (TextField): ユーザーの自己紹介。
        profile_image (ImageField): ユーザーのプロフィール画像。
        hobbies (TextField): ユーザーの趣味や興味。
        languages (TextField): ユーザーが話す言語。
        is_smoker (BooleanField): ユーザーが喫煙者かどうか。
        has_pets (BooleanField): ユーザーがペットを持っているかどうか。
        is_verified (BooleanField): ユーザーが本人確認を済ませているかどうか。
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_email = models.EmailField(null=True)
    user_first_name = models.CharField(max_length=30, null=True)
    user_last_name = models.CharField(max_length=30, null=True)
    sex = models.CharField(max_length=10, null=True)
    day_of_birth = models.DateField(null=True)
    age = models.IntegerField(null=True)
    profession = models.CharField(max_length=50, null=True)
    self_introduction = models.TextField(null=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    hobbies = models.TextField(null=True, blank=True)
    languages = models.TextField(null=True, blank=True)
    is_smoker = models.BooleanField(default=False)
    has_pets = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
