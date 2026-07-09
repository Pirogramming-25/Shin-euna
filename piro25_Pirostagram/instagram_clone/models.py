from django.db import models
from django.contrib.auth.models import User

'''
# 1. 유저 모델
class User(AbstractUser):
    name = models.CharField(help_text="사용자 이름")
    profile_img = models.ImageField(upload_to='profiles/', null=True)

    def __str__(self):
        return self.username
'''
# 2. 팔로우 모델
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'follower_set')
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} -> {self.following.username}"

# 3. 게시글 모델
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'posts')
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='posts/')

    def __block__(self):
        return f"{self.author.username}의 게시글 ({self.id})"
    
# 4. 좋아요 모델
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} liked Post {self.post.id}"

# 5. 댓글 모델
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on Post {self.post.id}"
    
# 6. 스토리 모델
class Story(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}의 스토리"

# 7. 스토리 상세 이미지 모델
class StoryImage(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='stories/')

