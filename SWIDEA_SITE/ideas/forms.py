from django import forms
from .models import Idea


class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ('title', 'image', 'content', 'interest', 'devtool')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '아이디어 제목'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': '아이디어 내용을 입력하세요'}),
            'interest': forms.NumberInput(attrs={'class': 'form-control'}),
            'devtool': forms.Select(attrs={'class': 'form-select'}),
        }
