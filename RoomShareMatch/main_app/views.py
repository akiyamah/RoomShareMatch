from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from RoomShareMatch.constants.instructions_data  import instructions
from django.db import IntegrityError, DatabaseError
from .forms import (
    UserUpdateForm, UserProfileForm, UserPurposeForm,
    UserDesiredCohabiteeForm, UserRoomLayoutForm, UserRentForm
)
from .models import (
    UserProfile, UserPurpose, UserDesiredCohabitee,
    UserRoomLayout, UserRent
)
from matching_app.models import RoommatePreference
from django.contrib import messages


def get_initial_model_form(request, model_class, form_class, field_name):
    """
    ユーザーに関連するデータを取得し、指定されたフォームクラスの初期化を行います。
    データは、指定されたモデルクラスとフィールド名に基づいてフィルタリングされます。
    (この処理はユーザー1対N個のデータ関係を持つmodelに対して繰り返し処理を行う際を想定して作成。)
    引数:
    request (HttpRequest): ユーザーからのリクエスト情報を含む HttpRequest オブジェクト。
    model_class (Model): データを取得するために使用されるモデルクラス。
    form_class (Form): データを初期化するために使用されるフォームクラス。
    field_name (str): モデルインスタンスから取得するフィールド名。
    
    戻り値:
    form (form_class): 初期化されたフォームクラスのインスタンス。
    
    例:
    user_data_form = get_initial_model_form(request, UserProfile, UserProfileForm, 'hobby')
    """
    objects = model_class.objects.filter(user=request.user)
    initial_model_form = form_class(initial={field_name: [getattr(object, field_name) for object in objects]})
    return initial_model_form


def get_matching_profile_context(request):
    # リクエストユーザーに関連するデータを取得し、初期化したフォームクラスを返す。
    purpose_form = get_initial_model_form(request, UserPurpose, UserPurposeForm, 'purpose_name')
    cohabitation_form = get_initial_model_form(request, UserDesiredCohabitee, UserDesiredCohabiteeForm, 'cohabitation_number')
    layout_form = get_initial_model_form(request, UserRoomLayout, UserRoomLayoutForm, 'layout')
    rent_form = get_initial_model_form(request, UserRent, UserRentForm, 'rent')
    user_profile_form = UserProfileForm(instance=UserProfile.objects.get(user=request.user))
    
    context = {
        'purpose_form': purpose_form,
        'cohabitation_form': cohabitation_form,
        'layout_form': layout_form,
        'rent_form': rent_form,
        'roommate_preference_form': user_profile_form,
    }
    return context


def update_user_data(request, model_class, model_form, field_name):
    # 既存のデータを削除してから新しいデータを保存
    try:
        model_class.objects.filter(user=request.user).delete()        
        dates = model_form.cleaned_data[field_name]
        for date in dates:
            instance = model_class(user=request.user, **{field_name: date})
            instance.save()
    except ValidationError as ve:
        raise ValueError(f"Validation error updating {model_class.__name__}: {str(ve)}")
    except Exception as e:
        raise ValueError(f"Error updating {model_class.__name__}: {str(e)}")


def signup(request):
    # POST時にバリテーションがTureであればユーザー登録を行い、ログイン状態でユーザーホーム画面を返す。
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('main_app:user_home')
        else:
            return render(request, 'main_app/signup.html', {'form': form})
    return render(request, 'main_app/signup.html')


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('main_app:user_home')
        else:
            messages.error(request, 'ログインに失敗しました。ユーザー名とパスワードを確認してください。')
            return render(request, 'main_app/login.html', {'form': form})
    else:
        form = AuthenticationForm()
        return render(request, 'main_app/login.html', {'form': form})


def logout(request):
    # ログアウト後、TOP画面を返す
    auth_logout(request)
    return redirect('main_app:signup')


@login_required
def user_home(request):
    # ユーザープロフィール、アプリの使用方法を表示
    user_profile = UserProfile.objects.get(user=request.user)
    context = {
        'user_profile': user_profile,
        'instructions': instructions
    }
    return render(request, 'main_app/user_home.html',context)


@login_required
def auth_info(request):
    # 認証情報の表示
    if request.method == 'GET':
        form = UserUpdateForm(instance=request.user)
        return render(request, 'main_app/auth_info.html', {'form': form})


@login_required
def update_auth_info(request):
    # 認証情報の更新
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                new_password = form.cleaned_data.get("new_password")
                if new_password:
                    user.set_password(new_password)
                user.save()
                
                if new_password:
                    messages.success(request, 'プロフィールが更新されました！再度ログインしてください。')
                    logout(request)
                    return redirect('main_app:login')
                else:
                    messages.success(request, 'プロフィールが更新されました！')
                    return redirect('main_app:auth_info')
                
            except IntegrityError as e:
                messages.error(request, f"データベースの整合性エラーが発生しました: {e}")
            except DatabaseError as e:
                messages.error(request, f"データベースエラーが発生しました: {e}")
            except Exception as e:
                messages.error(request, f"予期しないエラーが発生しました: {e}")
            return render(request, 'main_app/auth_info.html', {'form': form})
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'main_app/auth_info.html', {'form': form})
    return redirect('main_app:auth_info')



@login_required
def matching_profile(request):
    # リクエストユーザーに関連するデータを取得し、初期化したフォームクラスを返す。
    if request.method == 'GET':
        context = get_matching_profile_context(request)
        return render(request, 'main_app/matching_profile.html', context)


@login_required
def update_matching_profile(request):
    if request.method == 'POST':
        try:
            # PSOTされたデータのフォーム作成
            purpose_form = UserPurposeForm(request.POST)
            cohabitation_form = UserDesiredCohabiteeForm(request.POST)
            layout_form = UserRoomLayoutForm(request.POST)
            rent_form = UserRentForm(request.POST)
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            
            # バリデーション
            if (purpose_form.is_valid() and 
                cohabitation_form.is_valid() and
                layout_form.is_valid() and 
                rent_form.is_valid() and 
                user_profile_form.is_valid()):
                
                # 1対Nのモデルのデータを更新
                update_user_data(request, UserPurpose, purpose_form, 'purpose_name')
                update_user_data(request, UserDesiredCohabitee, cohabitation_form, 'cohabitation_number')
                update_user_data(request, UserRoomLayout, layout_form, 'layout')
                update_user_data(request, UserRent, rent_form, 'rent')
                
                # 1対1のモデルのデータを更新
                user_profile_form.save()
                
                messages.success(request, 'プロフィールが更新されました！')
        except ValueError as ve:
            messages.error(request, f"プロフィールの更新に失敗しました： {str(ve)}")
        
        # リクエストユーザーに関連するデータを取得し、初期化したフォームクラスを返す。
        context = get_matching_profile_context(request)
        return render(request, 'main_app/matching_profile.html', context)

