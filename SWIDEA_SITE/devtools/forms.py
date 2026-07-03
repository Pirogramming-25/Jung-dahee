from django import forms
from .models import DevTool


class DevToolForm(forms.ModelForm):
    class Meta:
        model = DevTool
        fields = ('name', 'kind', 'content')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '예: Django'}),
            'kind': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': '설명을 입력하세요'}),
        }
