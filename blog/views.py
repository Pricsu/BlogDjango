from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, PostComments, Likes
from .forms import PostCommentsForm, PostSearchForm
from users.models import Profile
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

class FollowingPostListView(ListView):
    model = Post
    template_name = 'blog/following_posts.html'
    paginate_by = 5
    context_object_name = 'posts'

    def get_queryset(self):
        profile = Profile.objects.get(pk=self.kwargs.get('pk'))
        profile_follows = profile.follows.all()
        profile_follows = [profile.user.pk for profile in profile_follows]
        return Post.objects.filter(author_id__in=profile_follows).order_by('-date_posted')


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_profile.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        profile = get_object_or_404(Profile, pk=self.kwargs.get('pk'))
        user = profile.user
        return Post.objects.filter(author=user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, pk=self.kwargs.get('pk'))
        context['profile'] = profile
        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            profile = get_object_or_404(Profile, pk=self.kwargs.get('pk'))
            current_user_profile = request.user.profile
            action = request.POST.get('follow')
            if action == 'unfollow':
                current_user_profile.follows.remove(profile)
            else:
                current_user_profile.follows.add(profile)
            current_user_profile.save()
        return self.get(request, *args, **kwargs)


# here we display the comments and the empty form
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        user = self.request.user
        liked = False
        if user.is_authenticated:
            if post.likes_set.filter(post=post, user=user).exists():
                liked = True
        ordered_comments = post.comments.order_by('-date_posted')
        context['comment_form'] = PostCommentsForm()
        context['comments'] = ordered_comments
        context['liked'] = liked
        return context

# if we create a comment we save the comment and redirect to the post-detail

@login_required
def add_comment_to_post(request, pk):

    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostCommentsForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect('post-detail', pk=pk)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PostComments

    def test_func(self):
        comment = self.get_object()
        if comment.author == self.request.user:
            return True
        return False

    def get_success_url(self):
        comment = self.get_object()
        return reverse_lazy('post-detail', kwargs={'pk': comment.post.pk})


class CommentUpdateView(UpdateView):
    model = PostComments
    fields = ['content']


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog-home')

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def about(request):
    return render(request, 'blog/about.html', {"title": "About"})


@login_required
def like_post(request, pk):

    post = get_object_or_404(Post, pk=pk)
    user = request.user

    if Likes.objects.filter(post=post, user=user).exists():
        like = Likes.objects.get(post=post, user=user)
        like.delete()
        liked = False
    else:
        Likes.objects.create(post=post, user=user)
        liked = True

    return redirect ('post-detail', pk=post.pk)


class PostSearchListView(ListView):
    model = Post
    template_name = 'blog/post_search.html'
    context_object_name = 'posts'

    def get_queryset(self):
        searched = self.request.GET.get('searched')
        if searched:
            return Post.objects.filter(title__icontains=searched).order_by("-date_posted")
        return Post.objects.none()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        searched = self.request.GET.get('searched')
        context['status_posts'] = self.object_list.exists()
        context['status_profiles'] = Profile.objects.filter(user__username__contains=searched).exists()
        context['searched'] = searched
        context['profiles'] = Profile.objects.filter(user__username__contains=searched)
        return context


class MostLikedPostsView(ListView):
    model = Post
    template_name = 'blog/most_liked_post.html'
    context_object_name = 'most_liked_posts'

    def get_queryset(self):
        return Post.objects.annotate(total_likes=Count('likes')).order_by('-total_likes')[:5]


class ProfileFollowersListView(ListView):
    model = Profile
    template_name = 'blog/profile_followers.html'
    context_object_name = 'followers'
    paginate_by = 8

    def get_queryset(self):
        profile = Profile.objects.get(pk=self.kwargs.get('pk'))
        return profile.followed_by.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = get_object_or_404(Profile, pk=self.kwargs.get('pk'))
        context['total_followers'] = profile_user.total_followers()
        return context


class ProfileFollowingListView(ListView):
    model = Profile
    template_name = 'blog/profile_following.html'
    context_object_name = 'following'
    paginate_by = 8

    def get_queryset(self):
        profile = Profile.objects.get(pk=self.kwargs.get('pk'))
        return profile.follows.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = get_object_or_404(Profile, pk=self.kwargs.get('pk'))
        context['total_following'] = profile_user.total_following()
        return context


