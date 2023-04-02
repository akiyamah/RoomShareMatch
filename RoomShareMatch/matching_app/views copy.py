from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from .forms import PurposeForm, DesiredCohabiteeForm, RoomLayoutForm, RentForm, RoommatePreferenceForm
from .models import Purpose, DesiredCohabitee, RoomLayout, Rent, RoommatePreference
from main_app.models import UserProfile
from django.shortcuts import render, get_object_or_404


@login_required
def roommate_preference_view(request):
    '''
    # 各モデルから情報を取得し、レンダリング処理したHTMLをリターン
    '''
    if request.method == 'GET':
        # Purpose
        purpose_choices = []
        purposes = Purpose.objects.filter(user=request.user)
        for purpose in purposes:
            purpose_choices.append(purpose.purpose_name)
        purpose_form = PurposeForm(initial={'purpose_name': purpose_choices or None})

        # DesiredCohabitee
        cohabitation_choices = []
        cohabitations = DesiredCohabitee.objects.filter(user=request.user)
        for cohabitation in cohabitations:
            cohabitation_choices.append(cohabitation.cohabitation_number)
        cohabitation_form = DesiredCohabiteeForm(initial={'cohabitation_number': cohabitation_choices or None})

        # RoomLayout
        layout_choices = []
        layouts = RoomLayout.objects.filter(user=request.user)
        for layout in layouts:
            layout_choices.append(layout.layout)
        layout_form = RoomLayoutForm(initial={'layout': layout_choices or None})

        # Rent
        rent_choices = []
        rents = Rent.objects.filter(user=request.user)
        for rent in rents:
            rent_choices.append(rent.rent)
        rent_form = RentForm(initial={'rent': rent_choices or None})
        
        # RoommatePreference
        roommate_preference, created = RoommatePreference.objects.get_or_create(user=request.user)
        roommate_preference_form = RoommatePreferenceForm(instance=roommate_preference)
        
        context = {
            'purpose_form': purpose_form,
            'cohabitation_form': cohabitation_form,
            'layout_form': layout_form,
            'rent_form': rent_form,
            'roommate_preference_form': roommate_preference_form,
        }
        return render(request, 'matching_app/roommate_preference.html', context)


@login_required
@transaction.atomic
def save_roommate_preference(request):
    if request.method == 'POST':
        purpose_form = PurposeForm(request.POST)
        cohabitation_form = DesiredCohabiteeForm(request.POST)
        layout_form = RoomLayoutForm(request.POST)
        rent_form = RentForm(request.POST)        
        roommate_preference_form = RoommatePreferenceForm(request.POST)
        
        if all([
            purpose_form.is_valid(), 
            cohabitation_form.is_valid(), 
            layout_form.is_valid(), 
            rent_form.is_valid(), 
            roommate_preference_form.is_valid()
            ]):
            # 一致する既存のデータを削除
            Purpose.objects.filter(user=request.user).delete()
            DesiredCohabitee.objects.filter(user=request.user).delete()
            RoomLayout.objects.filter(user=request.user).delete()
            Rent.objects.filter(user=request.user).delete()
            
            # RoommatePreferenceオブジェクトを削除し、新しいオブジェクトを作成
            RoommatePreference.objects.filter(user=request.user).delete()
            roommate_preference = roommate_preference_form.save(commit=False)
            roommate_preference.user = request.user
            roommate_preference.save()
            
            # 新しいデータを保存
            purpose_names = purpose_form.cleaned_data['purpose_name']
            for purpose_name in purpose_names:
                purpose_instance = Purpose(purpose_name=purpose_name, user=request.user)
                purpose_instance.save()
                
            cohabitation_numbers = cohabitation_form.cleaned_data['cohabitation_number']
            for cohabitation_number in cohabitation_numbers:
                cohabitation_instance = DesiredCohabitee(cohabitation_number=cohabitation_number, user=request.user)
                print(cohabitation_instance)
                cohabitation_instance.save()
                
            layout_choices = layout_form.cleaned_data['layout']
            for layout_choice in layout_choices:
                layout_instance = RoomLayout(layout=layout_choice, user=request.user)
                layout_instance.save()
                
            rent_choices = rent_form.cleaned_data['rent']
            for rent_choice in rent_choices:
                rent_instance = Rent(rent=rent_choice, user=request.user)
                rent_instance.save()
            
            success_message = 'プロフィールが更新されました！'
            context = {
                'purpose_form': purpose_form,
                'cohabitation_form': cohabitation_form,
                'layout_form': layout_form,
                'rent_form': rent_form,
                'roommate_preference_form': roommate_preference_form,
                'success_message': success_message
            }
            return render(request, 'main_app/roommate_preference.html', context)
    else:
        success_message = 'プロフィールが更新されませんでした！'
    return render(request, 'main_app/roommate_preference.html', context)



@login_required
def match_new(request):
    if request.method == 'GET':
        # DBからユーザーの登録日時が最新の10件を取得
        latest_users = User.objects.order_by('-date_joined')[:10]
        
        # ユーザーオブジェクトのユーザ名, 年齢のオブジェクトを作成
        users = []
        for user in latest_users:
            try:
                user_profile = UserProfile.objects.get(user=user)
                users.append({
                    'id': user.id,
                    'username': user.username,
                    'profile_image': user_profile.profile_image,
                    'age': user_profile.age,
                    'sex': user_profile.sex,
                })
            except UserProfile.DoesNotExist:
                continue
        
        # 10件のオブジェクトをmatch_new.htmlにレンダリングして返す。
        return render(request, 'matching_app/match_new.html', {'users': users})


@login_required
def match_recommend(request):
    if request.method == 'GET':
        # ユーザーに推奨されるマッチングを表示するためのロジックをここに実装します。
        return render(request, 'matching_app/match_recommend.html')


@login_required
def match_search(request):
    if request.method == 'GET':
        # ユーザーがマッチングを検索できるためのロジックをここに実装します。
        return render(request, 'matching_app/match_search.html')


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

