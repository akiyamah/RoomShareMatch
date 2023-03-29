from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import UserProfile




class UserUpdateForm(UserChangeForm):
    password = None  # パスワード変更を無効化
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class UserProfileForm(forms.ModelForm):
    UserProfile.clean_fields

    class Meta:
        model = UserProfile
        fields = [
            'user', 
            'user_email',
            'user_first_name',
            'user_last_name',
            'sex',
            'day_of_birth',
            'age',
            'profession',
            'self_introduction',
            'profile_image',
            'hobbies',
            'languages',
            'is_smoker',
            'has_pets',
            'is_verified',
        ]
        widgets = {
            'user_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'user_first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'user_last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'sex': forms.Select(attrs={'class': 'form-control'}),
            'day_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
            'self_introduction': forms.Textarea(attrs={'class': 'form-control'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'hobbies': forms.Textarea(attrs={'class': 'form-control'}),
            'languages': forms.Textarea(attrs={'class': 'form-control'}),
            'is_smoker': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_pets': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }