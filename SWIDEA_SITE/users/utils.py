from django.contrib.auth import get_user_model


def get_default_user():
    User = get_user_model()
    user, _ = User.objects.get_or_create(
        username='owner',
        defaults={'nickname': '나'},
    )
    return user