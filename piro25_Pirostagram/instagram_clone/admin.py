from django.contrib import admin
from .models import User, Post, Comment, Story, StoryImage

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Story)
admin.site.register(StoryImage)