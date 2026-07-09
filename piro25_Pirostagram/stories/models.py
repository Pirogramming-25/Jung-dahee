from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Story(models.Model):
    """한 유저가 특정 시점에 올린 스토리 묶음 (여러 장의 사진을 포함)."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username} story {self.id}'

    @property
    def is_active(self):
        return timezone.now() < self.created_at + timedelta(hours=24)


class StoryItem(models.Model):
    """스토리에 포함된 개별 사진 한 장."""

    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='items')
    image = models.ImageField(upload_to='story_images/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'item {self.id} of story {self.story_id}'
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Story(models.Model):
    """한 유저가 특정 시점에 올린 스토리 묶음 (여러 장의 사진을 포함)."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username} story {self.id}'

    @property
    def is_active(self):
        return timezone.now() < self.created_at + timedelta(hours=24)


class StoryItem(models.Model):
    """스토리에 포함된 개별 사진 한 장."""

    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='items')
    image = models.ImageField(upload_to='story_images/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'item {self.id} of story {self.story_id}'
