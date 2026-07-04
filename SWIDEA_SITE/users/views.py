from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import NicknameForm
from .utils import get_default_user


def settings_view(request):
    user = get_default_user()

    if request.method == 'POST':
        form = NicknameForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '닉네임이 저장되었습니다.')
            return redirect('idea_list')
    else:
        form = NicknameForm(instance=user)

    return render(request, 'users/settings.html', {'form': form})