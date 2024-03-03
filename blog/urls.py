from django.contrib import admin
from django.urls import path
from .views import (
    PostListView,
    FollowingPostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
    add_comment_to_post,
    CommentDeleteView,
    CommentUpdateView,
    like_post,
    PostSearchListView,
    MostLikedPostsView,
    ProfileFollowersListView,
    ProfileFollowingListView,
)
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name="blog-home"),
    path('following/<int:pk>/', FollowingPostListView.as_view(), name='following-posts'),
    path('profile/<int:pk>/', UserPostListView.as_view(), name='user-profile'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name="post-create"),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name="blog-about"),
    path('post/<int:pk>/comment/', add_comment_to_post, name='add-comment'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
    path('comment/<int:pk>/update/', CommentUpdateView.as_view(), name='comment-update'),
    path('post/<int:pk>/like/', like_post, name='like-post'),
    path('post/searched/', PostSearchListView.as_view(), name='post-search'),
    path('post/most-liked/', MostLikedPostsView.as_view(), name='most-liked'),
    path('profile/<int:pk>/followers/', ProfileFollowersListView.as_view(), name='profile-followers'),
    path('profile/<int:pk>/following/', ProfileFollowingListView.as_view(), name='profile-following'),
]
