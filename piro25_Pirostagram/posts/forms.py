from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('image', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'description'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': '댓글 달기...'}),
        }
