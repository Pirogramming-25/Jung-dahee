"""Custom access-control decorator.

`@login_required` alone redirects to LOGIN_URL with a `next` parameter but
gives us no easy way to also attach `required=1` so the login page can show
an alert ("로그인 후 이용해주세요"). This decorator handles both.
"""
from functools import wraps
from urllib.parse import urlencode

from django.shortcuts import redirect
from django.urls import reverse


def model_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        login_url = reverse("login")
        query = urlencode({"next": request.get_full_path(), "required": "1"})
        return redirect(f"{login_url}?{query}")

    return wrapper
