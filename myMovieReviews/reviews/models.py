from django.db import models

class MovieReview(models.Model):
    title = models.CharField(max_length=100)
    opening_year = models.IntegerField()
    director = models.CharField(max_length=50)
    actor = models.CharField(max_length=100)


    GENRE_CHOICES = [
        ('action', '액션'),
        ('romance', '로맨스/멜로'),
        ('comedy', '코미디'),
        ('thriller', '스릴러/공포'),
        ('sf', 'SF/판타지'),
        ('drama', '드라마'),
        ('animation', '애니메이션'),
    ]
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, default='action')

    star_rating = models.FloatField()
    running_time = models.IntegerField()

    def get_running_time_to_hours(self):
        hours = self.running_time // 60
        minutes = self.running_time % 60

        if hours == 0:
            return f"{minutes}분"
        return f"{hours}시간 {minutes}분"

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title