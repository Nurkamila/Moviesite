from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelformset_factory
from django.contrib import messages

from .models import *
from .forms import CreateVideoForm, UpdateVideoForm


def get_video_list(request):
    videos = Video.objects.all()
    return render(request, 'video_list.html', context={'videos': videos})


def get_video_detail(request, slug):
    video = get_object_or_404(Video, slug=slug)
    return render(request, 'video_detail.html', context={'video': video})


@login_required(login_url='login')
def create_video(request):
    if request.method == 'POST':
        form = CreateVideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            # product = Product.objects.create(**form.cleaned_data)
            return redirect(video.get_absolute_url())
    else:
        form = CreateVideoForm()

    return render(request, 'create_video.html', {'create_form': form})


def update_video(request, id):
    video = get_object_or_404(Video, id=id)
    if request.user == video.user:
        video_form = UpdateVideoForm(request.POST or None, request.FILES or None, instance=video)
        if video_form.is_valid():
            video = video_form.save()
            return redirect(video.get_absolute_url())
        return render(request, 'update_video.html', locals())
    else:
        return HttpResponse('<h1>403 Forbidden</h1>')


def detele_video(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if request.user == video.user:
        if request.method == 'POST':
            video.delete()
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted!')
            return redirect("video_list_url")
        return render(request, 'delete_video.html', locals())
    else:
        return HttpResponse('<h1>403 Forbidden</h1>')




def search_video(request):
    category = None
    categories = Category.objects.all()
    video = None
    search = request.GET.get('search')
    if search:
        video = Video.objects.filter(Q(title__icontains=search) |
                                          Q(description__icontains=search)
                                          )
    context = {
        'videos': video,
        'categories': categories,
        'category': category
    }
    return render(
        request,
        'video_list.html',
        context
    )