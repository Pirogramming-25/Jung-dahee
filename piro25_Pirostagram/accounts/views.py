
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView
 
from .forms import ProfileForm, SignUpForm
from .models import Follow
 
 
class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = '/'
 
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
 
 
class PirostagramLoginView(LoginView):
    template_name = 'accounts/login.html'
 
 
class PirostagramLogoutView(LogoutView):
    pass
 
 
@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.all()
    is_following = Follow.objects.filter(
        follower=request.user, following=profile_user
    ).exists()
    is_me = profile_user == request.user
    return render(
        request,
        'accounts/profile.html',
        {
            'profile_user': profile_user,
            'posts': posts,
            'is_following': is_following,
            'is_me': is_me,
        },
    )
 
 
@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form})
 
 
@login_required
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)
    if target != request.user:
        follow, created = Follow.objects.get_or_create(
            follower=request.user, following=target
        )
        if not created:
            follow.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        from django.http import JsonResponse
 
        is_following = Follow.objects.filter(
            follower=request.user, following=target
        ).exists()
        return JsonResponse(
            {
                'is_following': is_following,
                'follower_count': target.followers.count(),
            }
        )
    return redirect('accounts:profile', username=username)
 
 
@login_required
def user_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = list(
            User.objects.filter(
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            ).exclude(id=request.user.id)
        )
        following_ids = set(
            Follow.objects.filter(follower=request.user, following__in=results).values_list(
                'following_id', flat=True
            )
        )
        for u in results:
            u.is_following = u.id in following_ids
    return render(
        request, 'accounts/user_search.html', {'query': query, 'results': results}
    )
 
