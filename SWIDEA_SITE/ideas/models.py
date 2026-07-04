from django.db import models
from django.contrib.auth.models import User

class DevTool(models.Model):
    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=100)
    content = models.TextField()
    
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name

class Idea(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='ideas/', blank=True, null=True)
    content = models.TextField()
    interest = models.IntegerField(default = 0)
    
    devtool = models.ForeignKey(DevTool, on_delete=models.SET_NULL, null=True, blank=True)    
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __repr__(self):
        return self.title
    def __str__(self):
        return self.title
    

class IdeaStar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 🔗 아이디어와의 연결: 어떤 아이디어를 찜했는가? (아이디어 삭제시 찜 데이터도 삭제)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)

    # 한 유저가 같은 아이디어를 중복해서 찜하지 못하도록 고유성(Unique) 제약을 둡니다.
    class Meta:
        unique_together = ('user', 'idea')

    def __str__(self):
        return f"{self.user.username} ⭐️ {self.idea.title}"
            