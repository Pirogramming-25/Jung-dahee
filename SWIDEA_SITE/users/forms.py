from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class NicknameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('nickname',)
        widgets = {
            'nickname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '예: 홍길동',
                'maxlength': 30,
            }),
        }
        labels = {
            'nickname': '닉네임',
        }