from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StoryForm
from .models import Story, StoryItem


@login_required
def story_create(request):
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        images = request.FILES.getlist('images')
        if images:
            story = Story.objects.create(author=request.user)
            for i, image in enumerate(images):
                StoryItem.objects.create(story=story, image=image, order=i)
            return redirect('posts:home')
        form.add_error('images', '최소 한 장의 사진을 선택해주세요.')
    else:
        form = StoryForm()
    return render(request, 'stories/story_form.html', {'form': form})


@login_required
def story_view(request, pk):
    story = get_object_or_404(Story, pk=pk)
    author = story.author

    # 그 사람이 올린(만료되지 않은) 모든 스토리를 시간순으로 합쳐서
    # 하나의 이어보기 목록으로 만든다 (스토리를 여러 개 올렸어도 전부 넘겨볼 수 있도록).
    author_stories = (
        Story.objects.filter(author=author)
        .order_by('created_at')
        .prefetch_related('items')
    )
    flat_items = []
    for s in author_stories:
        if not s.is_active:
            continue
        for item in s.items.all().order_by('order', 'created_at'):
            flat_items.append({'story': s, 'item': item})

    return render(
        request,
        'stories/story_view.html',
        {'author': author, 'story': story, 'flat_items': flat_items},
    )


@login_required
def story_delete(request, pk):
    story = get_object_or_404(Story, pk=pk)
    if story.author != request.user:
        return HttpResponseForbidden('삭제 권한이 없습니다.')
    if request.method == 'POST':
        story.delete()
        return redirect('posts:home')
    return render(request, 'stories/story_confirm_delete.html', {'story': story})