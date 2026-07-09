from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Follow
from stories.models import Story

from .forms import CommentForm, PostForm
from .models import Comment, Like, Post


def _followed_ids(user):
    return Follow.objects.filter(follower=user).values_list('following_id', flat=True)


@login_required
def home(request):
    following_ids = list(_followed_ids(request.user))
    following_ids.append(request.user.id)

    posts = (
        Post.objects.filter(author_id__in=following_ids)
        .select_related('author', 'author__profile')
        .annotate(num_likes=Count('likes', distinct=True))
        .annotate(num_comments=Count('comments', distinct=True))
    )

    sort = request.GET.get('sort', 'latest')
    if sort == 'likes':
        posts = posts.order_by('-num_likes', '-created_at')
    elif sort == 'comments':
        posts = posts.order_by('-num_comments', '-created_at')
    else:
        sort = 'latest'
        posts = posts.order_by('-created_at')

    posts = list(posts)
    liked_ids = set(
        Like.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True)
    )
    for post in posts:
        post.is_liked = post.pk in liked_ids

    my_story = (
        Story.objects.filter(author=request.user).order_by('-created_at').first()
    )

    stories = (
        Story.objects.filter(author_id__in=following_ids)
        .exclude(author=request.user)
        .select_related('author', 'author__profile')
        .order_by('-created_at')
    )
    # 유저 별 최신 스토리 하나만 스토리 바에 노출
    seen = set()
    story_list = []
    for story in stories:
        if story.author_id in seen:
            continue
        seen.add(story.author_id)
        story_list.append(story)

    suggested_users = (
        User.objects.exclude(id__in=following_ids)
        .exclude(id=request.user.id)
        .order_by('?')[:3]
    )

    comment_form = CommentForm()

    return render(
        request,
        'posts/home.html',
        {
            'posts': posts,
            'stories': story_list,
            'my_story': my_story,
            'suggested_users': suggested_users,
            'sort': sort,
            'comment_form': comment_form,
        },
    )


@login_required
def post_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = (
            Post.objects.filter(description__icontains=query)
            .select_related('author', 'author__profile')
            .order_by('-created_at')
        )
        results = list(results)
        liked_ids = set(
            Like.objects.filter(user=request.user, post__in=results).values_list(
                'post_id', flat=True
            )
        )
        for post in results:
            post.is_liked = post.pk in liked_ids
    return render(
        request, 'posts/post_search.html', {'query': query, 'results': results}
    )


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:home')
    else:
        form = PostForm()
    return render(request, 'posts/post_form.html', {'form': form, 'mode': 'create'})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden('수정 권한이 없습니다.')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:home')
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/post_form.html', {'form': form, 'mode': 'edit', 'post': post})


@login_required
@require_POST
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden('삭제 권한이 없습니다.')
    post.delete()
    return redirect('posts:home')


@login_required
@require_POST
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'like_count': post.likes.count()})


@login_required
@require_POST
def comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return JsonResponse(
            {
                'id': comment.id,
                'author': comment.author.username,
                'content': comment.content,
                'comment_count': post.comments.count(),
            }
        )
    return JsonResponse({'errors': form.errors}, status=400)


@login_required
@require_POST
def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user:
        return JsonResponse({'error': '수정 권한이 없습니다.'}, status=403)
    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'error': '내용을 입력해주세요.'}, status=400)
    comment.content = content
    comment.save()
    return JsonResponse({'id': comment.id, 'content': comment.content})


@login_required
@require_POST
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user:
        return JsonResponse({'error': '삭제 권한이 없습니다.'}, status=403)
    post = comment.post
    comment.delete()
    return JsonResponse({'id': pk, 'comment_count': post.comments.count()})