from django.conf import settings
from django.db import models

from devtools.models import DevTool


class Idea(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='ideas/%Y/%m/', blank=True, null=True)
    content = models.TextField()
    interest = models.IntegerField(default=0)
    devtool = models.ForeignKey(
        DevTool, on_delete=models.SET_NULL, null=True, blank=True, related_name='ideas'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='ideas'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    star_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='IdeaStar', related_name='starred_ideas', blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def star_count(self):
        return self.idea_stars.count()

    def is_starred_by(self, user):
        if not user or not user.is_authenticated:
            return False
            
        return self.idea_stars.filter(user=user).exists()


class IdeaStar(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='idea_stars')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='idea_stars')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('idea', 'user')

    def __str__(self):
        return f'{self.user} ♥ {self.idea}'

