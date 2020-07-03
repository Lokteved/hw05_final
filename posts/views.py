from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

from .models import Post, Group, Follow
from .forms import PostForm, CommentForm


User = get_user_model()


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'group.html',
        {'group': group, 'page': page, 'paginator': paginator}
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(
        request, 'new_post.html',
        {'form': form, 'is_edit': False}
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        if request.user.follower.filter(author=author).exists():
            following = True
    return render(
        request, 'profile.html',
        {
            'author': author,
            'page': page,
            'paginator': paginator,
            'following': following
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    following = False
    if request.user.is_authenticated:
        if request.user.follower.filter(author=post.author).exists:
            following = True
    return render(
        request, 'post.html',
        {
            'post': post,
            'author': post.author,
            'comments': comments,
            'form': form,
            'following': following
        }
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post.author == request.user:
        if form.is_valid():
            form.save()
            return redirect('post', username, post_id)
        return render(
            request, 'new_post.html',
            {'form': form, 'post': post, 'is_edit': True}
        )
    else:
        return redirect('post', username, post_id)


def page_not_found(request, exception):
    return render(
        request, 'misc/404.html',
        {'path': request.path}, status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', username, post_id)
    return render(request, 'comments.html', {'form': form})


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'follow.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    following = get_object_or_404(User, username=username)
    if following == request.user:
        return redirect('profile', username)
    Follow.objects.get_or_create(user=request.user, author=following)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    unfollowing = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=unfollowing)
    if follow.exists():
        follow.delete()
    return redirect('profile', username)


@login_required
def post_delete(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user == post.author:
        post.delete()
        return redirect('profile', username)
