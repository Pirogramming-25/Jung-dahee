from django.shortcuts import render, redirect, get_object_or_404

from .forms import ReviewForm
from .models import Review

SORT_OPTIONS = {
    'title': 'title',
    'rating': '-rating',
    'running_time': 'running_time',
}


def review_list(request):
    sort = request.GET.get('sort', '')
    order_by = SORT_OPTIONS.get(sort, '-created_at')
    reviews = Review.objects.all().order_by(order_by)
    context = {
        'reviews': reviews,
        'sort': sort,
    }
    return render(request, 'reviews/review_list.html', context)


def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    context = {'review': review}
    return render(request, 'reviews/review_detail.html', context)


def review_create(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save()
            return redirect('reviews:review_list')
    else:
        form = ReviewForm()
    context = {'form': form, 'is_update': False}
    return render(request, 'reviews/review_form.html', context)


def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            review = form.save()
            return redirect('reviews:review_detail', pk=review.pk)
    else:
        form = ReviewForm(instance=review)
    context = {'form': form, 'is_update': True, 'review': review}
    return render(request, 'reviews/review_form.html', context)


def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.delete()
        return redirect('reviews:review_list')
    return redirect('reviews:review_detail', pk=pk)