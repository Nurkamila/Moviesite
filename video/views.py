from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from config import settings
from .models import *
from .forms import CreateVideoForm, UpdateVideoForm, CommentForm
from myuser.models import User

@login_required()
def like_video(request, pk):
    video = get_object_or_404(Video, id=pk)
    if Like.objects.filter(user=request.user, video=video).exists():
        Like.objects.get(user=request.user, video=video).delete()
    else:
        Like.objects.create(user=request.user, video=video)
    return redirect('video_detail_url', video.slug)


def get_video_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    videos = Video.objects.all()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        videos = videos.filter(category=category)

    paginator = Paginator(videos, settings.PAGINATOR_NUM)
    page_number = request.GET.get('page')
    videos = paginator.get_page(page_number)

    context = {
        'videos': videos,
        'categories': categories,
        'category': category,
    }

    return render(request, 'video_list.html', context=context)


def get_video_detail(request, slug):
    video = get_object_or_404(Video, slug=slug)
    comment = Comment.objects.filter(video=video)
    likes = video.likes.all().count()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comm = form.save(commit=False)
            comm.user = request.user
            comm.video = video
            comm.save()
    else:
        form = CommentForm()

    return render(request, 'video_detail.html', context={'video': video, 'form': form, 'comment': comment, 'likes':likes})


# @login_required(login_url='login')
def create_video(request):
    if request.method == 'POST':
        form = CreateVideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            video.save()
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
            video = video_form.save(commit=False)
            video.user = request.user
            video.save()
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


def delete_comment(request, id):
    comment = Comment.objects.get(id=id)
    video = Video.objects.get(comment=comment)
    Comment.objects.get(id=id).delete()
    return redirect(f'/video/video/{video.slug}/')

@login_required()
def fav(request, slug):
    video = Video.objects.get(slug=slug)
    if request.user.is_authenticated:
        if Fav.objects.filter(video=video, user=request.user).exists():
            Fav.objects.filter(video=video, user=request.user).delete()
        else:
            Fav.objects.create(video=video, user=request.user)

        return redirect(f'/video/video/{video.slug}/')
    return render(request, 'fav.html', {'fav': fav})