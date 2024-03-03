from django.contrib import admin
from .models import Post, PostComments, Likes

admin.site.register(Post)
admin.site.register(PostComments)
admin.site.register(Likes)