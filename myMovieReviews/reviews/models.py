from django.db import models


class Review(models.Model):
    GENRE_CHOICES = [
        ('action', '액션'),
        ('comedy', '코미디'),
        ('drama', '드라마'),
        ('romance', '로맨스'),
        ('thriller', '스릴러'),
        ('horror', '공포'),
        ('sf', 'SF'),
        ('animation', '애니메이션'),
        ('documentary', '다큐멘터리'),
        ('fantasy', '판타지'),
    ]

    RATING_CHOICES = [(i / 2, f'{i / 2}점') for i in range(1, 11)]  # 0.5 ~ 5.0

    title = models.CharField(max_length=100)
    release_year = models.PositiveIntegerField()
    director = models.CharField(max_length=100)
    main_actor = models.CharField(max_length=100)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    rating = models.FloatField(choices=RATING_CHOICES)
    running_time = models.PositiveIntegerField(help_text='분 단위로 입력해주세요.')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def running_time_display(self):
        hours = self.running_time // 60
        minutes = self.running_time % 60
        if hours and minutes:
            return f'{hours}시간 {minutes}분'
        elif hours:
            return f'{hours}시간'
        return f'{minutes}분'