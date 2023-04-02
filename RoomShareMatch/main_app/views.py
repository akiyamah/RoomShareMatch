from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

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

def index(request):
    return render(request, 'main_app/index.html')


def register(request):
    # POST時にバリテーションがTureであればユーザー登録を行い、ログイン状態でユーザーホーム画面を返す。
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('main_app:user_home_view')
        else:
            return render(request, 'main_app/register.html', {'form': form})
    return render(request, 'main_app/register.html')


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # ユーザー名の存在チェック
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'ユーザー名が存在しません。')
            return render(request, 'main_app/login.html', {'form': form})
        
        # パスワードの一致チェック
        user = User.objects.get(username=username)
        if not user.check_password(password):
            messages.error(request, 'パスワードが正しくありません。')
            return render(request, 'main_app/login.html', {'form': form})
        
        # 認証成功時の処理
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('main_app:user_home_view')
        else:
            messages.error(request, 'ログインに失敗しました。ユーザー名とパスワードを確認してください。')
            return render(request, 'main_app/login.html', {'form': form})
    return render(request, 'main_app/login.html')


def logout(request):
    # ログアウト後、TOP画面を返す
    auth_logout(request)
    return redirect('main_app:index')


@login_required
def user_home_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'main_app/user_home.html', {'user_profile': user_profile})


@login_required
def update_auth_info(request):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
    # 認証情報の表示及び更新
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data.get("new_password")
            if new_password:
                user.set_password(new_password)
            user.save()
            success_message = 'プロフィールが更新されました！'
            return render(request, 'main_app/update_auth_info.html', {'form': form, 'success_message': success_message})
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'main_app/update_auth_info.html', {'form': form})


def get_user_data(request, model_class, form_class, field_name):
    """
    ユーザーに関連するデータを取得し、指定されたフォームクラスの初期化を行います。
    データは、指定されたモデルクラスとフィールド名に基づいてフィルタリングされます。
    
    引数:
    request (HttpRequest): ユーザーからのリクエスト情報を含む HttpRequest オブジェクト。
    model_class (Model): データを取得するために使用されるモデルクラス。
    form_class (Form): データを初期化するために使用されるフォームクラス。
    field_name (str): モデルインスタンスから取得するフィールド名。
    
    戻り値:
    form (form_class): 初期化されたフォームクラスのインスタンス。
    
    例:
    user_data_form = get_user_data(request, UserProfile, UserProfileForm, 'hobby')
    """
    queryset = model_class.objects.filter(user=request.user)
    choices = [getattr(instance, field_name) for instance in queryset]
    form = form_class(initial={field_name: choices})
    return form


def get_matching_profile_context(request):
    user_purposes = UserPurpose.objects.filter(user=request.user)
    user_cohabitees = UserDesiredCohabitee.objects.filter(user=request.user)
    user_layouts = UserRoomLayout.objects.filter(user=request.user)
    user_rents = UserRent.objects.filter(user=request.user)

    purpose_form = UserPurposeForm(initial={'purpose_name': [p.purpose_name for p in user_purposes]})
    cohabitation_form = UserDesiredCohabiteeForm(initial={'cohabitation_number': [c.cohabitation_number for c in user_cohabitees]})
    layout_form = UserRoomLayoutForm(initial={'layout': [l.layout for l in user_layouts]})
    rent_form = UserRentForm(initial={'rent': [r.rent for r in user_rents]})

    user_profile = UserProfile.objects.get(user=request.user)
    user_profile_form = UserProfileForm(instance=user_profile)

    context = {
        'purpose_form': purpose_form,
        'cohabitation_form': cohabitation_form,
        'layout_form': layout_form,
        'rent_form': rent_form,
        'roommate_preference_form': user_profile_form,
    }
    return context


@login_required
def matching_profile_view(request):
    if request.method == 'GET':
        context = get_matching_profile_context(request)
        return render(request, 'main_app/matching_profile.html', context)

@login_required
def update_user_data(request, model_class, field_name, post_key):
    try:
        # 既存のデータを削除する
        model_class.objects.filter(user=request.user).delete()
        
        # 新しいデータを保存する
        selected_items = request.POST.getlist(post_key)
        for item in selected_items:
            instance = model_class(user=request.user, **{field_name: item})
            instance.full_clean()  # バリデーションチェック
            instance.save()
    except ValidationError as ve:
        raise ValueError(f"Validation error updating {model_class.__name__}: {str(ve)}")
    except Exception as e:
        raise ValueError(f"Error updating {model_class.__name__}: {str(e)}")


@login_required
def update_matching_profile(request):
    if request.method == 'POST':
        purpose_form = UserPurposeForm(request.POST)
        cohabitation_form = UserDesiredCohabiteeForm(request.POST)
        layout_form = UserRoomLayoutForm(request.POST)
        rent_form = UserRentForm(request.POST)
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if (purpose_form.is_valid() and cohabitation_form.is_valid() and
            layout_form.is_valid() and rent_form.is_valid() and user_profile_form.is_valid()):
            try:
                # 各モデルに対して関数を呼び出す
                update_user_data(request, UserPurpose, 'purpose_name', 'purpose_name')
                update_user_data(request, UserDesiredCohabitee, 'cohabitation_number', 'cohabitation_number')
                update_user_data(request, UserRoomLayout, 'layout', 'layout')
                update_user_data(request, UserRent, 'rent', 'rent')                
                user_profile_form.save()
                success_message = 'プロフィールが更新されました！'
            except ValueError as ve:
                success_message = f"プロフィールの更新に失敗しました： {str(ve)}"
            
            context = get_matching_profile_context(request)
            context['success_message'] = success_message
            return render(request, 'main_app/matching_profile.html', context)

