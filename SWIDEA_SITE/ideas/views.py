import json

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from users.utils import get_default_user
from .models import Idea, IdeaStar
from .forms import IdeaForm
from devtools.models import DevTool

PAGE_SIZE = 4

SORT_OPTIONS = {
    'latest': ('-created_at', '최신순'),
    'oldest': ('created_at', '등록순'),
    'title': ('title', '이름순'),
    'interest': ('-interest', '관심도순'),
    'star': (None, '찜하기순'),  # 별도 처리 (annotate)
}


def _get_filtered_queryset(request):
    from django.db.models import Count

    ideas = Idea.objects.select_related('devtool', 'author').annotate(star_total=Count('idea_stars'))

    q = request.GET.get('q', '').strip()
    devtool_id = request.GET.get('devtool', '').strip()

    if q:
        ideas = ideas.filter(title__icontains=q)
    if devtool_id:
        ideas = ideas.filter(devtool_id=devtool_id)

    sort = request.GET.get('sort', 'latest')
    if sort == 'star':
        ideas = ideas.order_by('-star_total', '-created_at')
    else:
        order_field, _ = SORT_OPTIONS.get(sort, SORT_OPTIONS['latest'])
        ideas = ideas.order_by(order_field)

    return ideas, sort, q, devtool_id


def _starred_ids():
    """단일 사용자 기준 찜한 아이디어 id 집합"""
    user = get_default_user()
    return set(IdeaStar.objects.filter(user=user).values_list('idea_id', flat=True))


def idea_list(request):
    ideas, sort, q, devtool_id = _get_filtered_queryset(request)

    paginator = Paginator(ideas, PAGE_SIZE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    user = get_default_user()

    context = {
        'page_obj': page_obj,
        'sort': sort,
        'sort_options': SORT_OPTIONS,
        'q': q,
        'devtool_id': devtool_id,
        'devtools': DevTool.objects.all(),
        'starred_ids': _starred_ids(),
        'nickname': user.nickname,
    }
    return render(request, 'ideas/idea_list.html', context)


def idea_search_ajax(request):
    """AJAX 검색/정렬/필터: 리스트 부분만 렌더링해서 반환"""
    ideas, sort, q, devtool_id = _get_filtered_queryset(request)

    paginator = Paginator(ideas, PAGE_SIZE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    html = render_to_string('ideas/_idea_list_partial.html', {
        'page_obj': page_obj,
        'sort': sort,
        'q': q,
        'devtool_id': devtool_id,
        'starred_ids': _starred_ids(),
    }, request=request)

    return JsonResponse({'html': html, 'count': paginator.count})


def idea_detail(request, pk):
    idea = get_object_or_404(Idea.objects.select_related('devtool', 'author'), pk=pk)
    context = {
        'idea': idea,
        'is_starred': idea.is_starred_by(get_default_user()),
    }
    return render(request, 'ideas/idea_detail.html', context)


def idea_create(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.author = get_default_user()
            idea.save()
            messages.success(request, '아이디어가 등록되었습니다.')
            return redirect('idea_detail', pk=idea.pk)
    else:
        form = IdeaForm()
    return render(request, 'ideas/idea_form.html', {'form': form, 'is_update': False})


def idea_update(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES, instance=idea)
        if form.is_valid():
            idea = form.save()
            messages.success(request, '아이디어가 수정되었습니다.')
            return redirect('idea_detail', pk=idea.pk)
    else:
        form = IdeaForm(instance=idea)
    return render(request, 'ideas/idea_form.html', {'form': form, 'is_update': True, 'idea': idea})


def idea_delete(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    if request.method == 'POST':
        idea.delete()
        messages.success(request, '아이디어가 삭제되었습니다.')
        return redirect('idea_list')
    return redirect('idea_detail', pk=pk)


@require_POST
def idea_star_toggle(request, pk):
    """AJAX: 찜 토글. 새로고침 없이 처리."""
    idea = get_object_or_404(Idea, pk=pk)
    user = get_default_user()
    star, created = IdeaStar.objects.get_or_create(idea=idea, user=user)
    if not created:
        star.delete()
        starred = False
    else:
        starred = True

    return JsonResponse({
        'starred': starred,
        'star_count': idea.star_count,
    })


@require_POST
def idea_interest_change(request, pk):
    """AJAX: 관심도 +/- 처리. 새로고침 없이 처리."""
    idea = get_object_or_404(Idea, pk=pk)

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        data = {}
    delta = data.get('delta', request.POST.get('delta', 1))

    try:
        delta = int(delta)
    except (TypeError, ValueError):
        delta = 0

    idea.interest = max(0, idea.interest + delta)
    idea.save(update_fields=['interest'])

    return JsonResponse({'interest': idea.interest})