from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .forms import PostForm, CommentForm
from .models import Post, Group, Comment, Follow


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('/')
    return render(request, 'new.html', {'form': form, 'is_edit': False})


def profile(request, username):
    author_profile = get_object_or_404(User, username=username)
    post = author_profile.posts.all()
    paginator = Paginator(post, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    subscription = False
    if request.user.is_authenticated:
        subscription = Follow.objects.filter(user=request.user,
                                             author=author_profile).exists()
    return render(request, 'profile.html', {
        'page': page,
        'profile': author_profile,
        'subscription': subscription,
    })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm()
    comments = Comment.objects.filter(post__id=post_id)
    return render(request, 'post.html', {'post': post,
                                         'form': form,
                                         'comments': comments,
                                         'profile': post.author})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post,
                             author__username=username,
                             id=post_id)
    if request.user == post.author:
        form = PostForm(data=request.POST or None,
                        files=request.FILES or None,
                        instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post', username=username, post_id=post_id)
        return render(request, 'new.html', {
            'form': form,
            'post': post,
            'is_edit': True
        })
    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (request.user != author and not
            Follow.objects.filter(user=request.user,
                                  author=author).exists()):
        Follow.objects.create(user=request.user, author=author)
        return redirect('follow_index')
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    subscribe = Follow.objects.filter(user=request.user,
                                      author__username=username)
    if subscribe.exists():
        subscribe.delete()
        return redirect('follow_index')
    return redirect('profile', username=username)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
