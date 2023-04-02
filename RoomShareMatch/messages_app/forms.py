# messages_app/forms.py

from django import forms
from .models import Message

class SendMessageForm(forms.ModelForm):
    content = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    image = forms.ImageField(required=False)

    class Meta:
        model = Message
        fields = ['content', 'image']
