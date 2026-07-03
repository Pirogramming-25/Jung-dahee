from django.db import models


class DevTool(models.Model):
    KIND_CHOICES = [
        ('language', '언어'),
        ('framework', '프레임워크'),
        ('library', '라이브러리'),
        ('database', '데이터베이스'),
        ('tool', '툴'),
        ('etc', '기타'),
    ]

    name = models.CharField(max_length=50)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default='etc')
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_kind_display_ko(self):
        return dict(self.KIND_CHOICES).get(self.kind, self.kind)