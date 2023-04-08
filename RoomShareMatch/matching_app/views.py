from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from .forms import PurposeForm, DesiredCohabiteeForm, RoomLayoutForm, RentForm, RoommatePreferenceForm
from .models import Purpose, DesiredCohabitee, RoomLayout, Rent, RoommatePreference
from main_app.models import UserProfile
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import date
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.contrib import messages
from main_app.views import get_initial_model_form, update_user_data
from sklearn.metrics.pairwise import cosine_similarity
from dateutil.relativedelta import relativedelta
import pandas as pd
from RoomShareMatch.constants.choices import (
    PURPOSE_CHOICES, DESIRED_COHABITEE_CHOICES, LAYOUT_CHOICES, RENT_CHOICES,
    GENDER_CHOICES, OCCUPATION_CHOICES, PREFECTURE_CHOICES, SMOKING_CHOICES,
    PET_CHOICES, PARKING_CHOICES, COMMUTE_TIME_CHOICES, PERIOD_CHOICES
)


def get_roommate_preference_context(request):
    # リクエストユーザーに関連するデータを取得し、初期化したフォームクラスを返す。
    purpose_form = get_initial_model_form(request, Purpose, PurposeForm, 'purpose_name')
    cohabitation_form = get_initial_model_form(request, DesiredCohabitee, DesiredCohabiteeForm, 'cohabitation_number')
    layout_form = get_initial_model_form(request, RoomLayout, RoomLayoutForm, 'layout')
    rent_form = get_initial_model_form(request, Rent, RentForm, 'rent')
    roommate_preference_form = RoommatePreferenceForm(instance=RoommatePreference.objects.get(user=request.user))
    
    context = {
        'purpose_form': purpose_form,
        'cohabitation_form': cohabitation_form,
        'layout_form': layout_form,
        'rent_form': rent_form,
        'roommate_preference_form': roommate_preference_form,
    }
    return context


@login_required
def roommate_preference(request):
    # リクエストユーザーに関連するデータを取得し、初期化したフォームクラスを返す。
    if request.method == 'GET':
        context = get_roommate_preference_context(request)
        return render(request, 'matching_app/roommate_preference.html', context)


@login_required
@transaction.atomic
def update_roommate_preference(request):
    if request.method == 'POST':
        try:
            # PSOTされたデータのフォーム作成
            purpose_form = PurposeForm(request.POST)
            cohabitation_form = DesiredCohabiteeForm(request.POST)
            layout_form = RoomLayoutForm(request.POST)
            rent_form = RentForm(request.POST)        
            roommate_preference_form = RoommatePreferenceForm(request.POST)
            roommate_preference_form = RoommatePreferenceForm(request.POST, instance=RoommatePreference.objects.get_or_create(user=request.user)[0])
            
            # バリデーション
            if (purpose_form.is_valid() and 
                cohabitation_form.is_valid() and 
                layout_form.is_valid() and 
                rent_form.is_valid() and 
                roommate_preference_form.is_valid()):
                
                # 1対Nのモデルのデータを更新
                update_user_data(request, Purpose, purpose_form, 'purpose_name')
                update_user_data(request, DesiredCohabitee, cohabitation_form, 'cohabitation_number')
                update_user_data(request, RoomLayout, layout_form, 'layout')
                update_user_data(request, Rent, rent_form, 'rent')
                
                # 1対1のモデルのデータを更新
                roommate_preference_form.save()
                
                messages.success(request, 'プロフィールが更新されました！')
        except ValueError as ve:
            messages.error(request, f"プロフィールの更新に失敗しました： {str(ve)}")
        
        context = get_roommate_preference_context(request)
        return render(request, 'matching_app/roommate_preference.html', context)


@login_required
def user_detail(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    user_profile = get_object_or_404(UserProfile, user=target_user)
    
    # Additional models
    roommate_preference = get_object_or_404(RoommatePreference, user=target_user)
    purposes = Purpose.objects.filter(user=target_user)
    desired_cohabitees = DesiredCohabitee.objects.filter(user=target_user)
    room_layouts = RoomLayout.objects.filter(user=target_user)
    rents = Rent.objects.filter(user=target_user)
    context = {
        'user': target_user,
        'profile': user_profile,
        'roommate_preference': roommate_preference,
        'purposes': purposes,
        'desired_cohabitees': desired_cohabitees,
        'room_layouts': room_layouts,
        'rents': rents,
    }
    return render(request, 'matching_app/user_detail.html', context)


@login_required
def match_new_users(request):
    """
    # Get the current page number from the query parameters, default is 1
    # DBからユーザーの登録日時が最新のユーザーを取得 (リクエストユーザーを除く)
    # Create a Paginator object with the users and the number of users per page
    # Get the users for the current page
    # ユーザーオブジェクトのユーザ名, 年齢のオブジェクトを作成
    """
    current_page = int(request.GET.get('page', 1))
    all_users = User.objects.exclude(pk=request.user.pk).order_by('-date_joined')
    paginator = Paginator(all_users, 5)
    latest_users = paginator.get_page(current_page)
    users = []
    for user in latest_users:
        try:
            user_profile = UserProfile.objects.get(user=user)
            users.append({
                'id': user.id,
                'user_name': user_profile.user_name,
                'profile_image': user_profile.profile_image,
                'age': user_profile.age,
                'sex': user_profile.sex,
            })
        except UserProfile.DoesNotExist:
            continue
    # Render the match_new.html template with the users and pagination information
    return render(request, 'matching_app/match_new.html', {
        'users': users,
        'current_page': current_page,
        'has_next': latest_users.has_next(),
        'has_previous': current_page > 1,  # 追加
    })


@login_required
def match_search_users(request):
    queryset = UserProfile.objects.exclude(user=request.user)
    search_params = {
        'keyword': request.GET.get('keyword', ''),
        'sex': request.GET.get('sex', ''),
        'min_age': request.GET.get('min_age', ''),
        'max_age': request.GET.get('max_age', ''),
        'prefecture': request.GET.get('prefecture', ''),
    }
    
    # Check if any search parameter is present
    if any(search_params.values()):
        if search_params['keyword']:
            queryset = queryset.filter(self_introduction__icontains=search_params['keyword'])
        if search_params['sex']:
            queryset = queryset.filter(sex=search_params['sex'])
        if search_params['min_age']:
            min_birthdate = date.today() - relativedelta(years=int(search_params['min_age']))
            queryset = queryset.filter(day_of_birth__lte=min_birthdate)
        if search_params['max_age']:
            max_birthdate = date.today() - relativedelta(years=int(search_params['max_age']) + 1) + timedelta(days=1)
            queryset = queryset.filter(day_of_birth__gt=max_birthdate)
        if search_params['prefecture']:
            queryset = queryset.filter(prefecture=search_params['prefecture'])

        users = [
            {
                'id': user.user.id,
                'username': user.user.username,
                'user_name': user.user_name,
                'profile_image': user.profile_image,
                'age': user.age,
                'sex': user.sex,
                'prefecture': user.prefecture,
                'self_introduction': user.self_introduction,
            }
            for user in queryset
        ]
    else:
        users = []

    context = {
        'users': users, 
        'search_params': search_params, 
        'prefecture_choices': PREFECTURE_CHOICES
    }
    return render(request, 'matching_app/match_search.html', context)








def get_filtered_users(request, queryset=None):
    if queryset is None:
        queryset = UserProfile.objects.exclude(user=request.user)
    search_params = request.GET
    if 'keyword' in search_params and search_params['keyword']:
        queryset = queryset.filter(Q(user_name__icontains=search_params['keyword']) | Q(self_introduction__icontains=search_params['keyword']))
    if 'sex' in search_params and search_params['sex']:
        queryset = queryset.filter(sex=search_params['sex'])
    if 'min_age' in search_params and search_params['min_age']:
        min_birthdate = date.today() - relativedelta(years=int(search_params['min_age']) + 1) + timedelta(days=1)
        queryset = queryset.filter(day_of_birth__gt=min_birthdate)
    if 'max_age' in search_params and search_params['max_age']:
        max_birthdate = date.today() - relativedelta(years=int(search_params['max_age']))
        queryset = queryset.filter(day_of_birth__lte=max_birthdate)
    users = []
    for user_profile in queryset:
        users.append({
            'id': user_profile.user.id,
            'username': user_profile.user.username,
            'profile_image': user_profile.profile_image,
            'age': user_profile.age,
            'sex': user_profile.sex,
        })
    return users



def calculate_cosine_similarity(a, b):
    return cosine_similarity([a], [b])[0][0]

from django.core.files import File
def match_recommend_users(request):
    # 前処理
    analyze_fields = {
        "sex": GENDER_CHOICES, 
        "prefecture": PREFECTURE_CHOICES, 
        "period": PERIOD_CHOICES,  
        "is_smoker": SMOKING_CHOICES, 
        "has_pets": PET_CHOICES, 
        "parking": PARKING_CHOICES,
    }

    field_dicts = {}
    for field, choices in analyze_fields.items():
        field_dict = {}
        for index, (value, _) in enumerate(choices):
            field_dict[value] = index
        field_dicts[field] = field_dict

    user_profiles = UserProfile.objects.exclude(user=request.user)

    numeric_profiles = []
    for profile in user_profiles:
        numeric_profile = {}
        for field in analyze_fields:
            field_dict = field_dicts[field]
            original_value = getattr(profile, field)
            numeric_value = field_dict.get(original_value, 0)  # デフォルト値を 0 に変更
            numeric_profile[field] = numeric_value
        numeric_profiles.append(numeric_profile)

    # 類似度計算
    request_user_profile = UserProfile.objects.get(user=request.user)
    numeric_request_user_profile = {field: field_dicts[field][getattr(request_user_profile, field)] for field in analyze_fields}
    similarities = []

    for numeric_profile in numeric_profiles:
        numeric_profile_values = list(numeric_profile.values())
        numeric_request_user_profile_values = list(numeric_request_user_profile.values())

        similarity = calculate_cosine_similarity(numeric_profile_values, numeric_request_user_profile_values)
        similarities.append(similarity)

    # レコメンデーションの生成
    user_profiles_with_similarity = list(zip(user_profiles, similarities))
    user_profiles_with_similarity.sort(key=lambda x: x[1], reverse=True)
    recommended_users = [user_profile for user_profile, similarity in user_profiles_with_similarity[:5]]

    # 結果の表示
    context = {
        "recommended_users": [
            {
                "id": user_profile.user.id,
                "user_name": user_profile.user.username,
                "profile_image": user_profile.profile_image.url if user_profile.profile_image else None,
                "age": user_profile.age,
                "sex": user_profile.sex,
                "similarity": round(similarity * 100, 2)  # 類似度を0-100%に変換し、小数点以下2桁まで表示
            }
            for user_profile, similarity in user_profiles_with_similarity[:5]  # recommended_usersリストを生成する代わりにここで直接ループ
        ]
    }

    
    return render(request, 'matching_app/match_recomend.html', context)


"""
def calculate_cosine_similarity(a, b):
    return cosine_similarity([a], [b])[0][0]

def match_recommend_users(request):
    '''
    目的:ユーザーにマッチした（類似した）思考やペルソナをリコメンドする。
        類似の嗜好を持つユーザーから推奨事項を生成します。(ユーザーベースの協調フィルタリング)
    処理ステップ:
    # データ取得: データベースからUserProfileオブジェクトを取得し、リクエストユーザー自身を除外
    # 前処理: 分類データを数値に変換し、類似度計算に適した形式に変形。
        データ
        モデル: UserProfile
        フィールド: sex, prefecture, period, is_smoker, has_pets, parking
    # 類似度計算: 各ユーザープロファイル間の類似度を計算し、類似度スコアを取得します。
    # 例えば、コサイン類似度を使用できます。
    # レコメンデーションの生成: 類似度スコアを降順にソートし、上位5件のユーザープロファイルを選択します。
    # 結果の表示: 選択されたユーザープロファイルをテンプレートに渡して、リコメンデーション結果を表示します。
    '''
    
    # ユーザープロファイルデータを取得
    user_profiles = UserProfile.objects.all()
    
    # ユーザープロファイルデータを取得し、リクエストユーザーを除外
    user_profiles = UserProfile.objects.exclude(user=request.user)
    
    # 前処理: 分類データを数値に変換し、類似度計算に適した形式に変形。
    '''
    対象のフィールド名: sex, prefecture, period, is_smoker, has_pets, parking
    対象のフィールドの取りうる値がタプルで形式で格納された値のリスト変数名: 
    GENDER_CHOICES, PREFECTURE_CHOICES, PERIOD_CHOICES, SMOKING_CHOICES, PET_CHOICES, PARKING_CHOICES
    例)
        GENDER_CHOICES = (
            ('男性', '男性'),
            ('女性', '女性'),
        )
    '''
    ### key=分類対象: str , value=選択肢: taple
    analyze_fields = {
        "sex": GENDER_CHOICES, 
        "prefecture": PREFECTURE_CHOICES, 
        "period": PERIOD_CHOICES,  
        "is_smoker": SMOKING_CHOICES, 
        "has_pets": PET_CHOICES, 
        "parking": PARKING_CHOICES,
    }
    
    # 各フィールドの分類データを数値に変換するための辞書を作成
    field_dicts = {}
    for field, choices in analyze_fields.items():
        field_dict = {}
        for index, (value, _) in enumerate(choices):
            field_dict[value] = index
        field_dicts[field] = field_dict
    
    # 例: {'sex': {'男性': 0, '女性': 1}, 'prefecture': {'東京': 0, '大阪': 1, '北海道': 2}, ...}
    print(field_dicts)
    
    # UserProfileオブジェクトの各フィールドを数値データに変換
    numeric_profiles = []
    for profile in user_profiles:
        numeric_profile = {}
        for field in analyze_fields:
            field_dict = field_dicts[field]
            original_value = getattr(profile, field)
            numeric_value = field_dict[original_value]
            numeric_profile[field] = numeric_value
        numeric_profiles.append(numeric_profile)
    
    # 例: [{'sex': 0, 'prefecture': 0, 'period': 1, 'is_smoker': 0, 'has_pets': 1, 'parking': 0}, ...]
    print(numeric_profiles)
    
    # 類似度計算
    request_user_profile = UserProfile.objects.get(user=request.user)
    numeric_request_user_profile = {field: field_dicts[field][getattr(request_user_profile, field)] for field in analyze_fields}
    similarities = []
    
    for numeric_profile in numeric_profiles:
        numeric_profile_values = list(numeric_profile.values())
        numeric_request_user_profile_values = list(numeric_request_user_profile.values())
        
        similarity = calculate_cosine_similarity(numeric_profile_values, numeric_request_user_profile_values)
        similarities.append(similarity)
        
    # 類似度を含む新しいリストを作成
    user_profiles_with_similarity = list(zip(user_profiles, similarities))
    
    # 類似度に基づいてユーザープロファイルをソート (降順)
    user_profiles_with_similarity.sort(key=lambda x: x[1], reverse=True)
    
    # 上位5件のユーザープロファイルを取得
    recommended_users = [user_profile for user_profile, similarity in user_profiles_with_similarity[:5]]
    
    # 例: [<UserProfile: user1>, <UserProfile: user2>, ...]
    print(recommended_users)
    
    # リコメンドユーザの特定の情報を返す。
    # 対象フィールド: id, user_name, profile_image, age, sex
    return render(request, 'matching_app/match_recomend.html', context)
"""