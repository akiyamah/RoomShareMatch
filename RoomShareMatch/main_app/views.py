from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserUpdateForm, UserProfileForm, UserPurposeForm, UserDesiredCohabiteeForm, UserRoomLayoutForm, UserRentForm
from .models import UserProfile, UserPurpose, UserDesiredCohabitee, UserRoomLayout, UserRent
from django.contrib.auth.models import User


def index(request):
    return render(request, 'main_app/index.html')


def register(request):
    '''
    GET時にユーザー登録画面を返す。
    POST時にバリテーションを行い、Tureであればユーザー登録後、ユーザーホーム画面を返す。
    バリテーションがFalseであればユーザー登録画面を返す。
    '''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('main_app:user_home')
        else:
            return render(request, 'main_app/register.html', {'form': form})
    return render(request, 'main_app/register.html')


def login(request):
    '''
    GET時にユーザーログイン画面を返す。
    POST時にバリテーションを行い、Tureであればログイン後、ユーザーホーム画面を返す。
    バリテーションがFalseであればユーザーログイン画面を返す。
    '''
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('main_app:user_home')
        else:
            return render(request, 'main_app/login.html', {'form': form})
    return render(request, 'main_app/login.html')


def logout(request):
    # ログアウト後、TOP画面を返す
    auth_logout(request)
    return redirect('main_app:index')


@login_required
def user_home(request):
    return render(request, 'main_app/user_home.html')


@login_required
def auth_info_edit(request):
    '''
    認証情報の更新を行う。
    GET時にユーザー情報を表示する画面を返す。
    POST時にバリテーションを行い、ユーザー情報を更新する。
    '''
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            success_message = 'プロフィールが更新されました！'
            return render(request, 'main_app/auth_info_edit.html', {'form': form, 'success_message': success_message})
    else: 
        form = UserUpdateForm(instance=request.user)
    return render(request, 'main_app/auth_info_edit.html', {'form': form})


@login_required
def matching_profile_edit(request):
    if request.method == 'GET':
        # UserPurposeForm
        purposes = UserPurpose.objects.filter(user=request.user)
        purpose_choices = [purpose.purpose_name for purpose in purposes]
        purpose_form = UserPurposeForm(initial={'purpose_name': purpose_choices})
        
        # UserDesiredCohabitee
        cohabitations = UserDesiredCohabitee.objects.filter(user=request.user)
        cohabitation_choices = [cohabitation.cohabitation_number for cohabitation in cohabitations]
        cohabitation_form = UserDesiredCohabiteeForm(initial={'cohabitation_number': cohabitation_choices})
        
        # UserRoomLayout
        layouts = UserRoomLayout.objects.filter(user=request.user)
        layout_choices = [layout.layout for layout in layouts]
        layout_form = UserRoomLayoutForm(initial={'layout': layout_choices})
        
        # UserRent
        rents = UserRent.objects.filter(user=request.user)
        rent_choices = [rent.rent for rent in rents]
        rent_form = UserRentForm(initial={'rent': rent_choices})
        
        # UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_profile_form = UserProfileForm(instance=user_profile)
        print(user_profile)
        
        context = {
            'purpose_form': purpose_form,
            'cohabitation_form': cohabitation_form,
            'layout_form': layout_form,
            'rent_form': rent_form,
            'roommate_preference_form': user_profile_form,
        }
        return render(request, 'main_app/matching_profile.html', context)
    
    if request.method == 'POST':
        print(request.POST)
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        purpose_form = UserPurposeForm(request.POST)
        cohabitation_form = UserDesiredCohabiteeForm(request.POST)
        layout_form = UserRoomLayoutForm(request.POST)
        rent_form = UserRentForm(request.POST)
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if (purpose_form.is_valid() and cohabitation_form.is_valid() and
            layout_form.is_valid() and rent_form.is_valid() and user_profile_form.is_valid()):
            
            # 既存のデータを削除する
            UserPurpose.objects.filter(user=request.user).delete()
            UserDesiredCohabitee.objects.filter(user=request.user).delete()
            UserRoomLayout.objects.filter(user=request.user).delete()
            UserRent.objects.filter(user=request.user).delete()
            
            # 新しいデータを保存する
            selected_purposes = request.POST.getlist('purpose_name')
            selected_cohabitation_numbers = request.POST.getlist('cohabitation_number')
            selected_layouts = request.POST.getlist('layout')
            selected_rents = request.POST.getlist('rent')
            
            for purpose in selected_purposes:
                user_purpose = UserPurpose(user=request.user, purpose_name=purpose)
                user_purpose.save()
                
            for cohabitation_number in selected_cohabitation_numbers:
                user_desired_cohabitee = UserDesiredCohabitee(user=request.user, cohabitation_number=cohabitation_number)
                user_desired_cohabitee.save()
                
            for layout in selected_layouts:
                user_room_layout = UserRoomLayout(user=request.user, layout=layout)
                user_room_layout.save()
                
            for rent in selected_rents:
                user_rent = UserRent(user=request.user, rent=rent)
                user_rent.save()
                
            saved_user_profile = user_profile_form.save()
            print('Saved user profile:', saved_user_profile)
            
            messages.success(request, 'プロフィール情報が保存されました。')
            return redirect('main_app:user_home')
        else:
            messages.error(request, 'エラーが発生しました。入力内容を確認してください。')
        
        context = {
            'purpose_form': purpose_form,
            'cohabitation_form': cohabitation_form,
            'layout_form': layout_form,
            'rent_form': rent_form,
            'roommate_preference_form': user_profile_form,
        }
        return render(request, 'main_app/matching_profile.html', context)

