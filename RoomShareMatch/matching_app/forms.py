from django import forms
from .models import Purpose, DesiredCohabitee, RoomLayout, Rent, RoommatePreference
from .choices import (
    PURPOSE_CHOICES, DESIRED_COHABITEE_CHOICES, LAYOUT_CHOICES, 
    RENT_CHOICES, GENDER_CHOICES, OCCUPATION_CHOICES, 
    PREFECTURE_CHOICES, SMOKING_CHOICES, PET_CHOICES, 
    PARKING_CHOICES, COMMUTE_TIME_CHOICES, PERIOD_CHOICES,AGE_CHOICES
)


class PurposeForm(forms.ModelForm):
    purpose_name = forms.MultipleChoiceField(
        choices=PURPOSE_CHOICES, 
        widget=forms.CheckboxSelectMultiple, 
        label='あなたが望むルームシェアの相手の目的は何ですか？'
    )
    
    class Meta:
        model = Purpose
        fields = ['purpose_name']

class DesiredCohabiteeForm(forms.ModelForm):
    cohabitation_number = forms.MultipleChoiceField(
        choices=DESIRED_COHABITEE_CHOICES, 
        widget=forms.CheckboxSelectMultiple, 
        label='あなたが望むルームシェアの相手の同居人数はどのくらいですか？'
    )
    
    class Meta:
        model = DesiredCohabitee
        fields = ['cohabitation_number']

class RoomLayoutForm(forms.ModelForm):
    layout = forms.MultipleChoiceField(
        choices=LAYOUT_CHOICES, 
        widget=forms.CheckboxSelectMultiple, 
        label='あなたが望むルームシェアの相手の希望間取りはどのようなものですか？'
    )
    
    class Meta:
        model = RoomLayout
        fields = ['layout']

class RentForm(forms.ModelForm):
    rent = forms.MultipleChoiceField(
        choices=RENT_CHOICES, 
        widget=forms.CheckboxSelectMultiple, 
        label='あなたが望むルームシェアの相手の家賃希望範囲はどのくらいですか？'
    )
    
    class Meta:
        model = Rent
        fields = ['rent']




class RoommatePreferenceForm(forms.ModelForm):
    class Meta:
        model = RoommatePreference
        fields = [
            'gender', 
            'age_min', 
            'age_max', 
            'occupation', 
            'period', 
            'prefecture', 
            'smoking', 
            'pet', 
            'commute_time',
            'parking', 
        ]
        labels = {
            'gender': 'どの性別のルームメイトを希望しますか？',
            'age_min': '希望するルームメイトの最小年齢は？',
            'age_max': '希望するルームメイトの最大年齢は？',
            'occupation': '希望するルームメイトの職業は？',
            'period': '希望するルームメイトの入居期間は？',
            'prefecture': '希望するルームメイトの都道府県は？',
            'smoking': '喫煙するルームメイトを希望しますか？',
            'pet': 'ペットを飼っているルームメイトを希望しますか？',
            'commute_time': '希望するルームメイトの最寄駅からの距離は？',
            'parking': '駐車場を利用するルームメイトを希望しますか？',
        }
        widgets = {
            'gender': forms.RadioSelect(choices=GENDER_CHOICES),
            'age_min': forms.Select(choices=AGE_CHOICES),
            'age_max': forms.Select(choices=AGE_CHOICES),
            'occupation': forms.RadioSelect(choices=OCCUPATION_CHOICES),
            'period': forms.RadioSelect(choices=PERIOD_CHOICES),
            'prefecture': forms.Select(choices=PREFECTURE_CHOICES),
            'smoking': forms.RadioSelect(choices=SMOKING_CHOICES),
            'pet': forms.RadioSelect(choices=PET_CHOICES),
            'commute_time': forms.RadioSelect(choices=COMMUTE_TIME_CHOICES),
            'parking': forms.RadioSelect(choices=PARKING_CHOICES),
        }
