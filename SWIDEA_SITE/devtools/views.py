from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .models import DevTool
from .forms import DevToolForm


def devtool_list(request):
    devtools = DevTool.objects.all()
    return render(request, 'devtools/devtool_list.html', {'devtools': devtools})


def devtool_detail(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    ideas = devtool.ideas.all()
    return render(request, 'devtools/devtool_detail.html', {
        'devtool': devtool,
        'ideas': ideas,
    })


def devtool_create(request):
    if request.method == 'POST':
        form = DevToolForm(request.POST)
        if form.is_valid():
            devtool = form.save()
            messages.success(request, '개발툴이 등록되었습니다.')
            return redirect('devtools:devtool_detail', pk=devtool.pk)
    else:
        form = DevToolForm()
    return render(request, 'devtools/devtool_form.html', {'form': form, 'is_update': False})


def devtool_update(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    if request.method == 'POST':
        form = DevToolForm(request.POST, instance=devtool)
        if form.is_valid():
            devtool = form.save()
            messages.success(request, '개발툴이 수정되었습니다.')
            return redirect('devtools:devtool_detail', pk=devtool.pk)
    else:
        form = DevToolForm(instance=devtool)
    return render(request, 'devtools/devtool_form.html', {'form': form, 'is_update': True, 'devtool': devtool})


def devtool_delete(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    if request.method == 'POST':
        devtool.delete()
        messages.success(request, '개발툴이 삭제되었습니다.')
        return redirect('devtools:devtool_list')
    return redirect('devtools:devtool_detail', pk=pk)