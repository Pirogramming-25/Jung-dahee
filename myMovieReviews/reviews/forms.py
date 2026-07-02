from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            'title',
            'release_year',
            'director',
            'main_actor',
            'genre',
            'rating',
            'running_time',
            'content',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '영화 제목'}),
            'release_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '개봉 년도'}),
            'director': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '감독'}),
            'main_actor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '주연'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'running_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '러닝타임 (분)'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': '리뷰 내용을 작성해주세요.'}),
        }
